"""Business logic for evidence."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Evidence, IngredientEvidence
from app.schemas import EvidenceReview


def list_evidence(
    db: Session,
    risk_level: str | None = None,
    study_type: str | None = None,
    year_min: int | None = None,
    year_max: int | None = None,
    ingredient_id: int | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Evidence]:
    q = db.query(Evidence)
    if risk_level:
        q = q.filter(Evidence.risk_level == risk_level)
    if study_type:
        q = q.filter(Evidence.study_type == study_type)
    if year_min:
        q = q.filter(Evidence.publication_year >= year_min)
    if year_max:
        q = q.filter(Evidence.publication_year <= year_max)
    if ingredient_id:
        q = q.join(IngredientEvidence).filter(IngredientEvidence.ingredient_id == ingredient_id)
    return q.order_by(Evidence.created_at.desc()).offset(skip).limit(limit).all()


def get_review_queue(db: Session, skip: int = 0, limit: int = 50) -> list[Evidence]:
    return (
        db.query(Evidence)
        .filter(Evidence.needs_review.is_(True))
        .order_by(Evidence.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def submit_review(db: Session, evidence_id: int, review: EvidenceReview) -> Evidence | None:
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        return None
    if review.risk_level is not None:
        evidence.risk_level = review.risk_level
    if review.risk_direction is not None:
        evidence.risk_direction = review.risk_direction
    if review.findings_summary is not None:
        evidence.findings_summary = review.findings_summary
    evidence.needs_review = review.needs_review
    evidence.processing_status = "reviewed"
    db.commit()
    db.refresh(evidence)
    return evidence


def get_evidence_for_ingredient(db: Session, ingredient_id: int) -> list[dict]:
    """Get evidence linked to an ingredient with relevance info."""
    rows = (
        db.query(Evidence, IngredientEvidence.relevance)
        .join(IngredientEvidence)
        .filter(IngredientEvidence.ingredient_id == ingredient_id)
        .order_by(Evidence.publication_year.desc().nullslast())
        .all()
    )
    return [{"evidence": e, "relevance": rel} for e, rel in rows]


def get_stats(db: Session) -> dict:
    evidence_count = db.query(func.count(Evidence.id)).scalar()
    review_count = db.query(func.count(Evidence.id)).filter(Evidence.needs_review.is_(True)).scalar()
    return {"evidence_count": evidence_count or 0, "review_count": review_count or 0}
