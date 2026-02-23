import logging
import threading
import traceback
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models import Evidence, Ingredient, IngredientEvidence, ProcessingJob
from app.schemas import EvidenceOut, FetchRequest, IngredientSummary, ProcessingJobOut
from app.services.ingredient_service import slugify

logger = logging.getLogger(__name__)

router = APIRouter(tags=["search"])


@router.get("/search")
def full_text_search(q: str, db: Session = Depends(get_db)):
    """Search across ingredients and evidence using LIKE."""
    pattern = f"%{q}%"

    ingredients = (
        db.query(Ingredient)
        .filter(
            or_(
                Ingredient.canonical_name.ilike(pattern),
                Ingredient.description.ilike(pattern),
            )
        )
        .limit(20)
        .all()
    )

    evidence = (
        db.query(Evidence)
        .filter(
            or_(
                Evidence.title.ilike(pattern),
                Evidence.abstract_english.ilike(pattern),
                Evidence.findings_summary.ilike(pattern),
            )
        )
        .limit(20)
        .all()
    )

    return {
        "ingredients": [IngredientSummary.model_validate(i) for i in ingredients],
        "evidence": [EvidenceOut.model_validate(e) for e in evidence],
    }


@router.post("/queries/generate")
def generate_search_queries(ingredient: str, database: str = "ebsco"):
    """Generate multilingual search queries via API."""
    from pipeline.query_generator import format_for_database
    from pipeline.query_generator import generate_queries as gen_queries

    queries = gen_queries(ingredient, use_ai=True)
    formatted = format_for_database(queries, database)
    return {"ingredient": ingredient, "database": database, "queries": formatted}


def _fetch_records(ingredient: str, sources: list[str], max_per_source: int) -> list[dict]:
    """Run fetchers for the given sources and return deduplicated records."""
    from app.config import settings
    from pipeline.query_generator import generate_queries

    queries = generate_queries(ingredient, use_ai=False)
    english_query = queries.get("en", f'"{ingredient}" AND ("cancer" OR "health risk" OR "toxicity")')

    all_records: list[dict] = []

    for source in sources:
        try:
            if source == "pubmed":
                from pipeline.pubmed_fetcher import PubMedFetcher

                fetcher = PubMedFetcher(
                    api_key=settings.pubmed_api_key,
                    email=settings.pubmed_email,
                )
                records = fetcher.search(english_query, max_results=max_per_source)

            elif source == "openalex":
                from pipeline.openalex_fetcher import OpenAlexFetcher

                fetcher = OpenAlexFetcher(
                    api_key=settings.openalex_api_key,
                    mailto=settings.pubmed_email,  # Reuse email for polite pool
                )
                records = fetcher.search(english_query, max_results=max_per_source)

            elif source == "scopus":
                from pipeline.scopus_fetcher import ScopusFetcher

                fetcher = ScopusFetcher(
                    api_key=settings.scopus_api_key,
                    insttoken=settings.scopus_insttoken,
                )
                records = fetcher.search(english_query, max_results=max_per_source)

            else:
                logger.warning("Unknown source: %s", source)
                continue

            all_records.extend(records)
        except Exception:
            logger.error("Fetcher %s failed:\n%s", source, traceback.format_exc())

    # Deduplicate by DOI across sources
    seen_dois: set[str] = set()
    unique_records: list[dict] = []
    for record in all_records:
        doi = record.get("doi")
        if doi:
            if doi in seen_dois:
                continue
            seen_dois.add(doi)
        unique_records.append(record)

    return unique_records


def _run_fetch_processing(job_id: int, ingredient: str, sources: list[str], max_per_source: int):
    """Run fetch + AI processing in a background thread."""
    from pipeline.ai_processor import process_paper, should_flag_for_review

    db = SessionLocal()
    job = db.query(ProcessingJob).get(job_id)
    if not job:
        db.close()
        return

    job.status = "processing"
    db.commit()

    try:
        records = _fetch_records(ingredient, sources, max_per_source)
    except Exception:
        logger.error("Fetch failed:\n%s", traceback.format_exc())
        job.status = "failed"
        db.commit()
        db.close()
        return

    job.total_records = len(records)
    db.commit()

    linked_ingredients: list[dict] = []

    for record in records:
        try:
            # Skip records with DOIs already in the database
            if record.get("doi"):
                existing = db.query(Evidence).filter(Evidence.doi == record["doi"]).first()
                if existing:
                    continue

            extraction = process_paper(record)

            if not extraction.is_food_safety_relevant:
                logger.info("Skipped irrelevant paper: %s", record.get("title", "")[:80])
                continue

            flagged = should_flag_for_review(extraction)

            evidence = Evidence(
                title=extraction.title_english,
                abstract_original=record.get("abstract"),
                abstract_english=extraction.abstract_english,
                authors=record.get("authors"),
                doi=record.get("doi"),
                journal=record.get("journal"),
                publication_year=record.get("year"),
                original_language=extraction.original_language,
                source_database=record.get("source_database"),
                study_type=extraction.study_type,
                findings_summary=extraction.findings_summary,
                risk_level=extraction.risk_level,
                risk_direction=extraction.risk_direction,
                confidence_score=extraction.confidence_score,
                conflict_of_interest=extraction.conflict_of_interest,
                url=record.get("url") or (f"https://doi.org/{record['doi']}" if record.get("doi") else None),
                plain_language_summary=extraction.plain_language_summary,
                needs_review=flagged,
                ris_raw=record.get("ris_raw"),
                processing_status="processed",
            )
            db.add(evidence)
            db.flush()

            for ing_found in extraction.ingredients_found:
                slug = slugify(ing_found.name)
                ingredient_obj = db.query(Ingredient).filter(Ingredient.slug == slug).first()
                if not ingredient_obj:
                    ingredient_obj = Ingredient(canonical_name=ing_found.name, slug=slug, evidence_count=0)
                    db.add(ingredient_obj)
                    db.flush()
                link = IngredientEvidence(
                    ingredient_id=ingredient_obj.id, evidence_id=evidence.id, relevance=ing_found.relevance
                )
                db.add(link)
                ingredient_obj.evidence_count += 1
                if {"name": ingredient_obj.canonical_name, "slug": ingredient_obj.slug} not in linked_ingredients:
                    linked_ingredients.append({"name": ingredient_obj.canonical_name, "slug": ingredient_obj.slug})

            job.processed_count += 1
            if flagged:
                job.flagged_count += 1
            db.commit()

        except Exception:
            logger.error("Processing record failed:\n%s", traceback.format_exc())
            db.rollback()
            job.failed_count += 1
            db.commit()

    job.result_ingredients = linked_ingredients
    job.status = "completed"
    job.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.close()


@router.post("/fetch", response_model=ProcessingJobOut)
def fetch_papers(req: FetchRequest, db: Session = Depends(get_db)):
    """Fetch papers from academic APIs and process them through the AI pipeline.

    Creates a ProcessingJob and runs fetching + processing in a background thread.
    Poll /processing/jobs/{id} for status.
    """
    valid_sources = {"pubmed", "openalex", "scopus"}
    for s in req.sources:
        if s not in valid_sources:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Unknown source: {s}. Valid: {', '.join(valid_sources)}")

    job = ProcessingJob(
        filename=f"fetch:{req.ingredient}",
        status="pending",
        total_records=0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    thread = threading.Thread(
        target=_run_fetch_processing,
        args=(job.id, req.ingredient, req.sources, req.max_per_source),
        daemon=True,
    )
    thread.start()

    job.status = "processing"
    db.commit()
    db.refresh(job)
    return job
