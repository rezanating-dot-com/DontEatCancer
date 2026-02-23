import logging
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models import Evidence, Ingredient, IngredientEvidence, ProcessingJob
from app.schemas import ProcessingJobOut

router = APIRouter(tags=["processing"])

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RIS_DIR = DATA_DIR / "ris_imports"
TEXT_DIR = DATA_DIR / "text_imports"


def _parse_text_to_record(filepath: Path) -> dict:
    """Parse a pasted text file into a record dict for the AI processor."""
    text = filepath.read_text(encoding="utf-8")
    return {
        "title": text[:200].split("\n")[0],  # first line as rough title
        "abstract": text,
        "authors": [],
        "journal": None,
        "year": None,
        "keywords": [],
        "source_database": "text-paste",
    }


def _run_processing(job_id: int):
    """Run processing in background thread."""
    from pipeline.ai_processor import process_paper, should_flag_for_review

    db = SessionLocal()
    job = db.query(ProcessingJob).get(job_id)
    if not job:
        db.close()
        return

    job.status = "processing"
    db.commit()

    is_text = job.filename.endswith(".txt")

    if is_text:
        filepath = TEXT_DIR / job.filename
        try:
            records = [_parse_text_to_record(filepath)]
        except Exception:
            job.status = "failed"
            db.commit()
            db.close()
            return
    else:
        from pipeline.ris_parser import parse_ris_file
        filepath = RIS_DIR / job.filename
        try:
            records = parse_ris_file(filepath)
        except Exception:
            job.status = "failed"
            db.commit()
            db.close()
            return

    linked_ingredients = []

    for record in records:
        try:
            extraction = process_paper(record)
            flagged = should_flag_for_review(extraction)

            if record.get("doi"):
                existing = db.query(Evidence).filter(Evidence.doi == record["doi"]).first()
                if existing:
                    continue

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
                slug = ing_found.name.lower().replace(" ", "-")
                ingredient = db.query(Ingredient).filter(Ingredient.slug == slug).first()
                if not ingredient:
                    ingredient = Ingredient(canonical_name=ing_found.name, slug=slug, evidence_count=0)
                    db.add(ingredient)
                    db.flush()
                link = IngredientEvidence(ingredient_id=ingredient.id, evidence_id=evidence.id, relevance=ing_found.relevance)
                db.add(link)
                ingredient.evidence_count += 1
                if {"name": ingredient.canonical_name, "slug": ingredient.slug} not in linked_ingredients:
                    linked_ingredients.append({"name": ingredient.canonical_name, "slug": ingredient.slug})

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


@router.get("/processing/jobs", response_model=list[ProcessingJobOut])
def list_jobs(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return db.query(ProcessingJob).order_by(ProcessingJob.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/processing/jobs/{job_id}", response_model=ProcessingJobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/processing/jobs/{job_id}/start", response_model=ProcessingJobOut)
def start_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "pending":
        raise HTTPException(status_code=400, detail=f"Job is already {job.status}")

    thread = threading.Thread(target=_run_processing, args=(job_id,), daemon=True)
    thread.start()

    job.status = "processing"
    db.commit()
    db.refresh(job)
    return job
