"""CLI tools for DontEatCancer data pipeline."""

import json
import re
import sys
from pathlib import Path

import typer

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

app = typer.Typer(help="DontEatCancer data pipeline tools")


def _normalize_name(name: str) -> str:
    """Strip E-numbers, parenthetical info, and extra whitespace from an ingredient name."""
    # Remove parenthetical suffixes like "(E 552)", "(E552)", "(INS 552)"
    name = re.sub(r"\s*\((?:E\s*\d+|INS\s*\d+)[^)]*\)", "", name, flags=re.IGNORECASE)
    return name.strip()


def _find_or_create_ingredient(db, name: str):
    """Find an existing ingredient by slug or alias, or create a new one."""
    from app.models import Ingredient, IngredientAlias
    from app.services.ingredient_service import slugify

    normalized = _normalize_name(name)
    slug = slugify(normalized)

    # 1. Exact slug match on normalized name
    ingredient = db.query(Ingredient).filter(Ingredient.slug == slug).first()
    if ingredient:
        return ingredient

    # 2. Try case-insensitive canonical name match
    ingredient = db.query(Ingredient).filter(
        Ingredient.canonical_name.ilike(normalized)
    ).first()
    if ingredient:
        return ingredient

    # 3. Check aliases
    alias = db.query(IngredientAlias).filter(
        IngredientAlias.alias_name.ilike(normalized)
    ).first()
    if alias:
        return db.query(Ingredient).filter(Ingredient.id == alias.ingredient_id).first()

    # 4. No match — create new ingredient
    ingredient = Ingredient(
        canonical_name=normalized,
        slug=slug,
        evidence_count=0,
    )
    db.add(ingredient)
    db.flush()
    return ingredient


@app.command()
def query(
    ingredient: str = typer.Argument(help="Ingredient name in English"),
    database: str = typer.Option("ebsco", help="Target database: ebsco, scopus, wos"),
    no_ai: bool = typer.Option(False, "--no-ai", help="Skip Claude API translation (use known translations only)"),
    output_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Generate multilingual search queries for an ingredient."""
    from pipeline.query_generator import LANGUAGE_NAMES, format_for_database, generate_queries

    queries = generate_queries(ingredient, use_ai=not no_ai)
    formatted = format_for_database(queries, database)

    if output_json:
        typer.echo(json.dumps(formatted, ensure_ascii=False, indent=2))
    else:
        typer.echo(f"\nSearch queries for: {ingredient}")
        typer.echo(f"Database format: {database.upper()}\n")
        typer.echo("=" * 60)
        for lang, q in formatted.items():
            lang_name = LANGUAGE_NAMES.get(lang, lang)
            typer.echo(f"\n[{lang_name}]")
            typer.echo(q)
        typer.echo("\n" + "=" * 60)


@app.command()
def parse(
    filepath: Path = typer.Argument(help="Path to RIS file"),
    output_json: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """Parse a RIS file and show extracted records."""
    from pipeline.ris_parser import parse_ris_file

    if not filepath.exists():
        typer.echo(f"Error: File not found: {filepath}", err=True)
        raise typer.Exit(1)

    records = parse_ris_file(filepath)
    typer.echo(f"Parsed {len(records)} records from {filepath.name}\n")

    if output_json:
        # Serialize without ris_raw for readability
        for r in records:
            r.pop("ris_raw", None)
        typer.echo(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        for i, r in enumerate(records, 1):
            typer.echo(f"{i}. {r['title']}")
            if r.get("doi"):
                typer.echo(f"   DOI: {r['doi']}")
            if r.get("year"):
                typer.echo(f"   Year: {r['year']}")
            if r.get("authors"):
                typer.echo(f"   Authors: {', '.join(r['authors'][:3])}{'...' if len(r['authors']) > 3 else ''}")
            typer.echo()


@app.command()
def process(
    filepath: Path = typer.Argument(help="Path to RIS file"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Parse only, don't call AI or save to DB"),
    limit: int = typer.Option(0, "--limit", help="Process only first N records (0 = all)"),
    no_fulltext: bool = typer.Option(False, "--no-fulltext", help="Skip full-text fetching"),
):
    """Process a RIS file through the full pipeline: parse → AI extract → save to DB."""
    from sqlalchemy.orm import Session

    from app.database import SessionLocal
    from app.models import Evidence, IngredientEvidence, ProcessingJob
    from pipeline.ai_processor import process_paper, should_flag_for_review
    from pipeline.ris_parser import parse_ris_file

    if not filepath.exists():
        typer.echo(f"Error: File not found: {filepath}", err=True)
        raise typer.Exit(1)

    records = parse_ris_file(filepath)
    if limit > 0:
        records = records[:limit]

    typer.echo(f"Parsed {len(records)} records from {filepath.name}")

    if dry_run:
        typer.echo("Dry run — skipping AI processing and database save.")
        for i, r in enumerate(records, 1):
            typer.echo(f"  {i}. {r['title'][:80]}")
        return

    db: Session = SessionLocal()
    job = ProcessingJob(filename=filepath.name, status="processing", total_records=len(records))
    db.add(job)
    db.commit()

    for i, record in enumerate(records, 1):
        typer.echo(f"[{i}/{len(records)}] Processing: {record['title'][:60]}...")
        try:
            extraction = process_paper(record)

            if not extraction.is_food_safety_relevant:
                typer.echo("  Skipped (not relevant to food safety)")
                continue

            flagged = should_flag_for_review(extraction)

            # Check for duplicate DOI
            if record.get("doi"):
                existing = db.query(Evidence).filter(Evidence.doi == record["doi"]).first()
                if existing:
                    typer.echo(f"  Skipped (duplicate DOI: {record['doi']})")
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
                plain_language_summary=extraction.plain_language_summary,
                url=record.get("url") or (f"https://doi.org/{record['doi']}" if record.get("doi") else None),
                needs_review=flagged,
                ris_raw=record.get("ris_raw"),
                processing_status="processed",
            )
            db.add(evidence)
            db.flush()

            # Fetch full text if enabled
            if not no_fulltext:
                from pipeline.fulltext_fetcher import fetch_fulltext
                full_text = fetch_fulltext(record)
                if full_text:
                    evidence.full_text = full_text
                    typer.echo(f"  Full text fetched ({len(full_text):,} chars)")
                else:
                    typer.echo("  No full text available")

            # Link to ingredients
            for ing_found in extraction.ingredients_found:
                ingredient = _find_or_create_ingredient(db, ing_found.name)

                link = IngredientEvidence(
                    ingredient_id=ingredient.id,
                    evidence_id=evidence.id,
                    relevance=ing_found.relevance,
                )
                db.add(link)
                ingredient.evidence_count += 1

            job.processed_count += 1
            if flagged:
                job.flagged_count += 1
                typer.echo(f"  Flagged for review (confidence: {extraction.confidence_score:.2f})")
            else:
                typer.echo(f"  OK (risk: {extraction.risk_level}, confidence: {extraction.confidence_score:.2f})")

            db.commit()

        except Exception as e:
            job.failed_count += 1
            db.commit()
            typer.echo(f"  FAILED: {e}", err=True)

    from datetime import datetime, timezone
    job.status = "completed"
    job.completed_at = datetime.now(timezone.utc)
    db.commit()

    processed = job.processed_count
    failed = job.failed_count
    flagged = job.flagged_count
    db.close()

    typer.echo(f"\nDone! Processed: {processed}, Failed: {failed}, Flagged: {flagged}")


@app.command()
def fetch(
    ingredient: str = typer.Argument(help="Ingredient name to search for"),
    source: list[str] = typer.Option(
        ["pubmed", "openalex", "scopus"],
        "--source",
        help="Sources to fetch from (repeat for multiple)",
    ),
    limit: int = typer.Option(50, "--limit", help="Max results per source"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Fetch and display only, don't process or save"),
    no_fulltext: bool = typer.Option(False, "--no-fulltext", help="Skip full-text fetching"),
):
    """Fetch papers from academic APIs (PubMed, OpenAlex, Scopus)."""
    from app.routers.search import _fetch_records

    typer.echo(f"Fetching papers for: {ingredient}")
    typer.echo(f"Sources: {', '.join(source)}")
    typer.echo(f"Max per source: {limit}\n")

    try:
        records = _fetch_records(ingredient, source, limit)
    except Exception as e:
        typer.echo(f"Error fetching records: {e}", err=True)
        raise typer.Exit(1)

    typer.echo(f"Fetched {len(records)} unique records\n")

    if not records:
        typer.echo("No results found.")
        return

    if dry_run:
        typer.echo("Dry run — showing fetched records:\n")
        for i, r in enumerate(records, 1):
            typer.echo(f"  {i}. [{r.get('source_database', '?')}] {r['title'][:80]}")
            if r.get("doi"):
                typer.echo(f"     DOI: {r['doi']}")
            if r.get("year"):
                typer.echo(f"     Year: {r['year']}")
            if r.get("authors"):
                typer.echo(f"     Authors: {', '.join(r['authors'][:3])}{'...' if len(r['authors']) > 3 else ''}")
            typer.echo()
        return

    # Full processing pipeline
    from datetime import datetime, timezone

    from sqlalchemy.orm import Session

    from app.database import SessionLocal
    from app.models import Evidence, Ingredient, IngredientEvidence, ProcessingJob
    from app.services.ingredient_service import slugify
    from pipeline.ai_processor import process_paper, should_flag_for_review

    db: Session = SessionLocal()
    job = ProcessingJob(
        filename=f"fetch:{ingredient}",
        status="processing",
        total_records=len(records),
    )
    db.add(job)
    db.commit()

    for i, record in enumerate(records, 1):
        typer.echo(f"[{i}/{len(records)}] Processing: {record['title'][:60]}...")
        try:
            # Skip duplicates by DOI
            if record.get("doi"):
                existing = db.query(Evidence).filter(Evidence.doi == record["doi"]).first()
                if existing:
                    typer.echo(f"  Skipped (duplicate DOI: {record['doi']})")
                    continue

            extraction = process_paper(record)

            if not extraction.is_food_safety_relevant:
                typer.echo("  Skipped (not relevant to food safety)")
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
                plain_language_summary=extraction.plain_language_summary,
                url=record.get("url") or (f"https://doi.org/{record['doi']}" if record.get("doi") else None),
                needs_review=flagged,
                ris_raw=record.get("ris_raw"),
                processing_status="processed",
            )
            db.add(evidence)
            db.flush()

            # Fetch full text if enabled
            if not no_fulltext:
                from pipeline.fulltext_fetcher import fetch_fulltext
                full_text = fetch_fulltext(record)
                if full_text:
                    evidence.full_text = full_text
                    typer.echo(f"  Full text fetched ({len(full_text):,} chars)")
                else:
                    typer.echo("  No full text available")

            for ing_found in extraction.ingredients_found:
                slug = slugify(ing_found.name)
                ingredient_obj = db.query(Ingredient).filter(Ingredient.slug == slug).first()
                if not ingredient_obj:
                    ingredient_obj = Ingredient(
                        canonical_name=ing_found.name,
                        slug=slug,
                        evidence_count=0,
                    )
                    db.add(ingredient_obj)
                    db.flush()

                link = IngredientEvidence(
                    ingredient_id=ingredient_obj.id,
                    evidence_id=evidence.id,
                    relevance=ing_found.relevance,
                )
                db.add(link)
                ingredient_obj.evidence_count += 1

            job.processed_count += 1
            if flagged:
                job.flagged_count += 1
                typer.echo(f"  Flagged for review (confidence: {extraction.confidence_score:.2f})")
            else:
                typer.echo(f"  OK (risk: {extraction.risk_level}, confidence: {extraction.confidence_score:.2f})")

            db.commit()

        except Exception as e:
            job.failed_count += 1
            db.commit()
            typer.echo(f"  FAILED: {e}", err=True)

    job.status = "completed"
    job.completed_at = datetime.now(timezone.utc)
    db.commit()

    processed = job.processed_count
    failed = job.failed_count
    flagged = job.flagged_count
    db.close()

    typer.echo(f"\nDone! Processed: {processed}, Failed: {failed}, Flagged: {flagged}")


if __name__ == "__main__":
    app()
