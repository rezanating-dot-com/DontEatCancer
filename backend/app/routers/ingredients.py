from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import IngredientCreate, IngredientDetail, IngredientSummary
from app.schemas.evidence import EvidenceOut
from app.services import evidence_service, ingredient_service

router = APIRouter(tags=["ingredients"])


@router.get("/ingredients", response_model=list[IngredientSummary])
def list_ingredients(
    category: str | None = None,
    risk_level: str | None = None,
    letter: str | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return ingredient_service.list_ingredients(db, category, risk_level, letter, skip, limit)


@router.post("/ingredients", response_model=IngredientDetail, status_code=201)
def create_ingredient(data: IngredientCreate, db: Session = Depends(get_db)):
    return ingredient_service.create_ingredient(db, data)


@router.get("/ingredients/categories", response_model=list[str])
def get_categories(db: Session = Depends(get_db)):
    return ingredient_service.get_categories(db)


@router.get("/ingredients/{slug}", response_model=IngredientDetail)
def get_ingredient(slug: str, db: Session = Depends(get_db)):
    ingredient = ingredient_service.get_ingredient_by_slug(db, slug)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    return ingredient


@router.get("/ingredients/{slug}/evidence")
def get_ingredient_evidence(slug: str, db: Session = Depends(get_db)):
    ingredient = ingredient_service.get_ingredient_by_slug(db, slug)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")
    results = evidence_service.get_evidence_for_ingredient(db, ingredient.id)
    return [
        {"evidence": EvidenceOut.model_validate(r["evidence"]), "relevance": r["relevance"]}
        for r in results
    ]
