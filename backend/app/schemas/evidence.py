from datetime import datetime

from pydantic import BaseModel


class EvidenceOut(BaseModel):
    id: int
    title: str
    abstract_english: str | None
    authors: list[str] | None
    doi: str | None
    journal: str | None
    publication_year: int | None
    original_language: str | None
    source_database: str | None
    study_type: str | None
    findings_summary: str | None
    risk_level: str | None
    risk_direction: str | None
    confidence_score: float | None
    conflict_of_interest: str | None
    url: str | None
    full_text: str | None
    plain_language_summary: str | None
    needs_review: bool
    processing_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class EvidenceReview(BaseModel):
    risk_level: str | None = None
    risk_direction: str | None = None
    findings_summary: str | None = None
    plain_language_summary: str | None = None
    url: str | None = None
    full_text: str | None = None
    needs_review: bool = False


class ResultIngredient(BaseModel):
    name: str
    slug: str


class ProcessingJobOut(BaseModel):
    id: int
    filename: str
    status: str
    total_records: int
    processed_count: int
    failed_count: int
    flagged_count: int
    result_ingredients: list[ResultIngredient] | None = None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
