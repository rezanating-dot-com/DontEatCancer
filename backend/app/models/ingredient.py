from sqlalchemy import ForeignKey, String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True)
    canonical_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    cas_number: Mapped[str | None] = mapped_column(String(50))
    e_number: Mapped[str | None] = mapped_column(String(20))
    category: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    overall_risk_level: Mapped[str | None] = mapped_column(String(20))  # safe, low, moderate, high, insufficient
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)

    aliases: Mapped[list["IngredientAlias"]] = relationship(back_populates="ingredient", cascade="all, delete-orphan")
    evidence_links: Mapped[list["IngredientEvidence"]] = relationship(back_populates="ingredient")


class IngredientAlias(Base):
    __tablename__ = "ingredient_aliases"

    id: Mapped[int] = mapped_column(primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"))
    alias_name: Mapped[str] = mapped_column(String(255), index=True)
    language: Mapped[str] = mapped_column(String(10))  # ISO 639-1
    is_primary: Mapped[bool] = mapped_column(default=False)

    ingredient: Mapped["Ingredient"] = relationship(back_populates="aliases")
