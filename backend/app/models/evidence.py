from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    abstract_original: Mapped[str | None] = mapped_column(Text)
    abstract_english: Mapped[str | None] = mapped_column(Text)
    authors: Mapped[list | None] = mapped_column(JSON)  # stored as JSON array
    doi: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    journal: Mapped[str | None] = mapped_column(String(500))
    publication_year: Mapped[int | None] = mapped_column(Integer)
    original_language: Mapped[str | None] = mapped_column(String(10))
    source_database: Mapped[str | None] = mapped_column(String(50))  # ebsco, scopus, wos, pubmed
    study_type: Mapped[str | None] = mapped_column(String(50))  # meta-analysis, cohort, case-control, in-vitro, review, etc.
    findings_summary: Mapped[str | None] = mapped_column(Text)
    risk_level: Mapped[str | None] = mapped_column(String(20))  # safe, low, moderate, high, insufficient
    risk_direction: Mapped[str | None] = mapped_column(String(20))  # increases, decreases, neutral, inconclusive
    confidence_score: Mapped[float | None] = mapped_column(Float)
    conflict_of_interest: Mapped[str | None] = mapped_column(Text)
    needs_review: Mapped[bool] = mapped_column(default=False)
    ris_raw: Mapped[dict | None] = mapped_column(JSON)
    processing_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, processed, failed, reviewed
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    ingredient_links: Mapped[list["IngredientEvidence"]] = relationship(back_populates="evidence")


class IngredientEvidence(Base):
    __tablename__ = "ingredient_evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"))
    evidence_id: Mapped[int] = mapped_column(ForeignKey("evidence.id", ondelete="CASCADE"))
    relevance: Mapped[str] = mapped_column(String(20), default="primary")  # primary, secondary, mentioned

    ingredient: Mapped["Ingredient"] = relationship(back_populates="evidence_links")
    evidence: Mapped["Evidence"] = relationship(back_populates="ingredient_links")


class ProcessingJob(Base):
    __tablename__ = "processing_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, processing, completed, failed
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    processed_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    flagged_count: Mapped[int] = mapped_column(Integer, default=0)
    result_ingredients: Mapped[list | None] = mapped_column(JSON)  # [{name, slug}]
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
