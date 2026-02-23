from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Evidence, Ingredient, IngredientEvidence
from app.schemas import EvidenceOut, EvidenceReview
from app.services import evidence_service

router = APIRouter(tags=["evidence"])


@router.get("/evidence/{evidence_id}", response_model=None)
def get_evidence(evidence_id: int, db: Session = Depends(get_db)):
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    links = (
        db.query(Ingredient.canonical_name, Ingredient.slug, IngredientEvidence.relevance)
        .join(IngredientEvidence)
        .filter(IngredientEvidence.evidence_id == evidence_id)
        .all()
    )
    out = EvidenceOut.model_validate(evidence).model_dump()
    out["ingredients"] = [
        {"name": name, "slug": slug, "relevance": rel} for name, slug, rel in links
    ]
    return out


@router.get("/evidence", response_model=list[EvidenceOut])
def list_evidence(
    risk_level: str | None = None,
    study_type: str | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    return evidence_service.list_evidence(db, risk_level, study_type, year_min, year_max, skip=skip, limit=limit)


@router.get("/evidence/review-queue", response_model=list[EvidenceOut])
def review_queue(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    return evidence_service.get_review_queue(db, skip, limit)


@router.patch("/evidence/{evidence_id}/review", response_model=EvidenceOut)
def submit_review(evidence_id: int, review: EvidenceReview, db: Session = Depends(get_db)):
    result = evidence_service.submit_review(db, evidence_id, review)
    if not result:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return result
