"""AI processing pipeline using Ollama for paper extraction and classification."""

import json

from openai import OpenAI
from pydantic import BaseModel

from app.config import settings

EXTRACTION_PROMPT = """You are analyzing a scientific paper to determine if it is about food ingredients/additives and their health effects (especially cancer risk).

FIRST: Decide if this paper is relevant. A paper is relevant ONLY if it studies the health or safety effects of a substance that humans consume as a food ingredient, food additive, or food contaminant. Papers about pharmaceuticals, surgical procedures, non-food industrial chemicals, or topics unrelated to food safety are NOT relevant.

Given the paper information below, extract structured data. If the paper is not in English, translate the title and abstract to English.

Paper information:
Title: {title}
Abstract: {abstract}
Authors: {authors}
Journal: {journal}
Year: {year}
Keywords: {keywords}

Return a JSON object with these fields:
- "is_food_safety_relevant": true if the paper is about a food ingredient/additive/contaminant and its health effects, false otherwise. If false, you may leave other fields minimal.
- "original_language": ISO 639-1 code (e.g., "en", "zh", "ar", "fr", "de")
- "title_english": English translation of the title (or original if already English)
- "abstract_english": English translation of the abstract (or original if already English)
- "ingredients_found": list of objects, each with:
  - "name": canonical English name of the food ingredient/additive
  - "relevance": "primary" (main subject), "secondary" (significantly discussed), or "mentioned" (briefly referenced)
- "study_type": one of "meta-analysis", "systematic-review", "cohort", "case-control", "cross-sectional", "in-vitro", "in-vivo", "review", "other"
- "findings_summary": 2-3 sentence summary of key findings related to health/cancer risk
- "risk_level": overall risk assessment: "safe", "low", "moderate", "high", or "insufficient"
- "risk_direction": "increases" (increases cancer/health risk), "decreases" (protective), "neutral", or "inconclusive"
- "conflict_of_interest": a plain-English summary of any conflicts of interest disclosed by the authors (e.g., "Funded by Coca-Cola", "Lead author consults for food additive manufacturer"). If none disclosed or not mentioned, use null.
- "plain_language_summary": 1-2 sentences explaining what this study means for an average person's health in simple, non-technical language. Focus on practical takeaways (e.g., "This study suggests eating large amounts of X may slightly increase cancer risk, but the evidence is not strong enough to draw firm conclusions.")
- "confidence_score": your confidence in this extraction from 0.0 to 1.0

If the paper has no abstract, set confidence_score to at most 0.5.
If no food ingredients are found, return an empty ingredients_found list and set confidence_score to at most 0.3.
Return ONLY the JSON object, no other text."""


class IngredientFound(BaseModel):
    name: str
    relevance: str  # primary, secondary, mentioned


class PaperExtraction(BaseModel):
    is_food_safety_relevant: bool = True
    original_language: str
    title_english: str
    abstract_english: str | None
    ingredients_found: list[IngredientFound]
    study_type: str | None
    findings_summary: str | None
    risk_level: str | None
    risk_direction: str | None
    conflict_of_interest: str | None = None
    plain_language_summary: str | None = None
    confidence_score: float


def process_paper(record: dict) -> PaperExtraction:
    """Process a single paper record through Ollama and return structured extraction."""
    client = OpenAI(
        api_key="ollama",
        base_url="http://localhost:11434/v1",
    )

    prompt = EXTRACTION_PROMPT.format(
        title=record.get("title", ""),
        abstract=record.get("abstract", "N/A"),
        authors=", ".join(record.get("authors", [])),
        journal=record.get("journal", "N/A"),
        year=record.get("year", "N/A"),
        keywords=", ".join(record.get("keywords", [])),
    )

    response = client.chat.completions.create(
        model="gemma3:27b",
        max_tokens=1500,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.choices[0].message.content.strip()
    # Extract JSON from response
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    if "{" in text:
        text = text[text.index("{"):text.rindex("}") + 1]

    data = json.loads(text)
    return PaperExtraction(**data)


def should_flag_for_review(extraction: PaperExtraction) -> bool:
    """Determine if a paper extraction should be flagged for human review."""
    if extraction.confidence_score < 0.7:
        return True
    if not extraction.ingredients_found:
        return True
    if extraction.risk_direction == "inconclusive":
        return True
    if extraction.abstract_english is None:
        return True
    if extraction.conflict_of_interest:
        return True
    return False
