"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-02-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ingredients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("canonical_name", sa.String(255), nullable=False, unique=True),
        sa.Column("slug", sa.String(255), nullable=False, unique=True),
        sa.Column("cas_number", sa.String(50)),
        sa.Column("e_number", sa.String(20)),
        sa.Column("category", sa.String(100)),
        sa.Column("description", sa.Text()),
        sa.Column("overall_risk_level", sa.String(20)),
        sa.Column("evidence_count", sa.Integer(), server_default="0"),
    )
    op.create_index("ix_ingredients_canonical_name", "ingredients", ["canonical_name"])
    op.create_index("ix_ingredients_slug", "ingredients", ["slug"])

    op.create_table(
        "ingredient_aliases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("alias_name", sa.String(255), nullable=False),
        sa.Column("language", sa.String(10), nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default="false"),
    )
    op.create_index("ix_ingredient_aliases_alias_name", "ingredient_aliases", ["alias_name"])

    op.create_table(
        "evidence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("abstract_original", sa.Text()),
        sa.Column("abstract_english", sa.Text()),
        sa.Column("authors", postgresql.ARRAY(sa.String())),
        sa.Column("doi", sa.String(255), unique=True),
        sa.Column("journal", sa.String(500)),
        sa.Column("publication_year", sa.Integer()),
        sa.Column("original_language", sa.String(10)),
        sa.Column("source_database", sa.String(50)),
        sa.Column("study_type", sa.String(50)),
        sa.Column("findings_summary", sa.Text()),
        sa.Column("risk_level", sa.String(20)),
        sa.Column("risk_direction", sa.String(20)),
        sa.Column("confidence_score", sa.Float()),
        sa.Column("needs_review", sa.Boolean(), server_default="false"),
        sa.Column("ris_raw", postgresql.JSONB()),
        sa.Column("processing_status", sa.String(20), server_default="'pending'"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_evidence_doi", "evidence", ["doi"])

    op.create_table(
        "ingredient_evidence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ingredient_id", sa.Integer(), sa.ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence_id", sa.Integer(), sa.ForeignKey("evidence.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relevance", sa.String(20), server_default="'primary'"),
    )

    op.create_table(
        "processing_jobs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("status", sa.String(20), server_default="'pending'"),
        sa.Column("total_records", sa.Integer(), server_default="0"),
        sa.Column("processed_count", sa.Integer(), server_default="0"),
        sa.Column("failed_count", sa.Integer(), server_default="0"),
        sa.Column("flagged_count", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )

    # Full-text search indexes using GIN with to_tsvector
    op.execute("""
        CREATE INDEX ix_ingredients_fts ON ingredients
        USING gin(to_tsvector('english', coalesce(canonical_name, '') || ' ' || coalesce(description, '')))
    """)
    op.execute("""
        CREATE INDEX ix_evidence_fts ON evidence
        USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(abstract_english, '') || ' ' || coalesce(findings_summary, '')))
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_evidence_fts")
    op.execute("DROP INDEX IF EXISTS ix_ingredients_fts")
    op.drop_table("processing_jobs")
    op.drop_table("ingredient_evidence")
    op.drop_table("evidence")
    op.drop_table("ingredient_aliases")
    op.drop_table("ingredients")
