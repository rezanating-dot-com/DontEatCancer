"""Business logic for ingredients."""

import re

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import Ingredient, IngredientAlias
from app.schemas import IngredientCreate


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    return slug.strip("-")


def list_ingredients(
    db: Session,
    category: str | None = None,
    risk_level: str | None = None,
    letter: str | None = None,
    skip: int = 0,
    limit: int = 50,
) -> list[Ingredient]:
    q = db.query(Ingredient)
    if category:
        q = q.filter(Ingredient.category == category)
    if risk_level:
        q = q.filter(Ingredient.overall_risk_level == risk_level)
    if letter:
        q = q.filter(Ingredient.canonical_name.ilike(f"{letter}%"))
    return q.order_by(Ingredient.canonical_name).offset(skip).limit(limit).all()


def get_ingredient_by_slug(db: Session, slug: str) -> Ingredient | None:
    return (
        db.query(Ingredient)
        .options(joinedload(Ingredient.aliases))
        .filter(Ingredient.slug == slug)
        .first()
    )


def create_ingredient(db: Session, data: IngredientCreate) -> Ingredient:
    ingredient = Ingredient(
        canonical_name=data.canonical_name,
        slug=slugify(data.canonical_name),
        cas_number=data.cas_number,
        e_number=data.e_number,
        category=data.category,
        description=data.description,
        overall_risk_level=data.overall_risk_level,
    )
    db.add(ingredient)
    db.flush()

    for alias_data in data.aliases:
        alias = IngredientAlias(
            ingredient_id=ingredient.id,
            alias_name=alias_data.alias_name,
            language=alias_data.language,
            is_primary=alias_data.is_primary,
        )
        db.add(alias)

    db.commit()
    db.refresh(ingredient)
    return ingredient


def get_categories(db: Session) -> list[str]:
    rows = (
        db.query(Ingredient.category)
        .filter(Ingredient.category.isnot(None))
        .distinct()
        .order_by(Ingredient.category)
        .all()
    )
    return [r[0] for r in rows]


def get_stats(db: Session) -> dict:
    ingredient_count = db.query(func.count(Ingredient.id)).scalar()
    return {"ingredient_count": ingredient_count or 0}
