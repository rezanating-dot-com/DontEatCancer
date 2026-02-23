from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Evidence, Ingredient
from app.schemas import EvidenceOut, IngredientSummary

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
