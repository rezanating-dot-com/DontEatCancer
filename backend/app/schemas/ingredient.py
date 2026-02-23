from pydantic import BaseModel


class AliasBase(BaseModel):
    alias_name: str
    language: str
    is_primary: bool = False


class AliasOut(AliasBase):
    id: int
    model_config = {"from_attributes": True}


class IngredientCreate(BaseModel):
    canonical_name: str
    cas_number: str | None = None
    e_number: str | None = None
    category: str | None = None
    description: str | None = None
    overall_risk_level: str | None = None
    aliases: list[AliasBase] = []


class IngredientSummary(BaseModel):
    id: int
    canonical_name: str
    slug: str
    cas_number: str | None
    e_number: str | None
    category: str | None
    overall_risk_level: str | None
    evidence_count: int

    model_config = {"from_attributes": True}


class IngredientDetail(IngredientSummary):
    description: str | None
    aliases: list[AliasOut]

    model_config = {"from_attributes": True}
