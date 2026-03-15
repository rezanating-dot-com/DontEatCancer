import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from openai import OpenAI
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import IngredientCreate, IngredientDetail, IngredientSummary
from app.schemas.evidence import EvidenceOut
from app.services import evidence_service, ingredient_service

logger = logging.getLogger(__name__)
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


OVERVIEW_PROMPT = """You are writing a plain-language overview of a food additive/ingredient for a consumer safety website. Base your overview on the ACTUAL RESEARCH below — do not make up information. Write in simple, clear language that a non-scientist can understand.

Ingredient: {name}
E-number: {e_number}
CAS number: {cas_number}
Category: {category}
Known aliases: {aliases}

=== RESEARCH EVIDENCE ({evidence_count} papers) ===
{evidence_text}
=== END RESEARCH ===

Using the research above as your primary source, return a JSON object with these fields:
- "what_it_is": 2-3 sentences explaining what this chemical is in simple terms. Draw from how the papers describe it. No jargon.
- "what_its_used_for": 2-3 sentences on why it's added to food (its function as an additive). Reference what the studies say about its use.
- "common_foods": a list of 8-12 specific common foods/products it's typically found in. Pull from the research when possible (e.g., specific products mentioned in exposure studies).
- "other_names": a list of other names, trade names, or abbreviations this ingredient goes by. Include any synonyms mentioned in the papers.
- "regulatory_status": 2-3 sentences on its current regulatory status. If the research mentions bans, EFSA/FDA evaluations, or regulatory changes, cite those specifically.
- "quick_safety_note": 2-3 sentences giving a balanced, honest summary grounded in what these specific studies found. Mention the range of findings (e.g., "X out of Y studies found..."). Don't be alarmist or dismissive — be factual and cite the evidence.

Return ONLY the JSON object, no other text."""


def _build_evidence_text(db: Session, ingredient_id: int) -> str:
    """Build a text summary of linked evidence for the overview prompt."""
    results = evidence_service.get_evidence_for_ingredient(db, ingredient_id)
    if not results:
        return "No research papers linked yet."

    parts = []
    for i, r in enumerate(results, 1):
        ev = r["evidence"]
        lines = [f"Paper {i}: {ev.title}"]
        if ev.journal:
            lines.append(f"  Journal: {ev.journal}")
        if ev.publication_year:
            lines.append(f"  Year: {ev.publication_year}")
        if ev.study_type:
            lines.append(f"  Study type: {ev.study_type}")
        if ev.risk_level:
            lines.append(f"  Risk level: {ev.risk_level}")
        if ev.risk_direction:
            lines.append(f"  Risk direction: {ev.risk_direction}")
        if ev.findings_summary:
            lines.append(f"  Findings: {ev.findings_summary}")
        if ev.abstract_english:
            # Include first 500 chars of abstract for richer context
            abstract = ev.abstract_english[:500]
            if len(ev.abstract_english) > 500:
                abstract += "..."
            lines.append(f"  Abstract: {abstract}")
        if ev.plain_language_summary:
            lines.append(f"  Plain summary: {ev.plain_language_summary}")
        if ev.conflict_of_interest:
            lines.append(f"  Conflicts: {ev.conflict_of_interest}")
        parts.append("\n".join(lines))

    return "\n\n".join(parts)


@router.post("/ingredients/{slug}/generate-overview")
def generate_overview(slug: str, db: Session = Depends(get_db)):
    """Generate a plain-language overview grounded in linked research papers."""

    ingredient = ingredient_service.get_ingredient_by_slug(db, slug)
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    aliases_str = ", ".join(
        f"{a.alias_name} ({a.language})" for a in ingredient.aliases
    )

    evidence_text = _build_evidence_text(db, ingredient.id)
    evidence_count = len(evidence_service.get_evidence_for_ingredient(db, ingredient.id))

    prompt = OVERVIEW_PROMPT.format(
        name=ingredient.canonical_name,
        e_number=ingredient.e_number or "N/A",
        cas_number=ingredient.cas_number or "N/A",
        category=ingredient.category or "N/A",
        aliases=aliases_str or "None known",
        evidence_text=evidence_text,
        evidence_count=evidence_count,
    )

    client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
    response = client.chat.completions.create(
        model="gemma3:27b",
        max_tokens=2000,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.choices[0].message.content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    if "{" in text:
        text = text[text.index("{"):text.rindex("}") + 1]

    overview = json.loads(text)

    # Save to description field as JSON
    ingredient.description = json.dumps(overview, ensure_ascii=False)
    db.commit()
    db.refresh(ingredient)

    return overview
