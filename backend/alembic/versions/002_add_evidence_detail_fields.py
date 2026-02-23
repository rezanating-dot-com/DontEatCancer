"""Add url, full_text, plain_language_summary to evidence

Revision ID: 002
Revises: 001
Create Date: 2026-02-22
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("evidence", sa.Column("url", sa.String(2000)))
    op.add_column("evidence", sa.Column("full_text", sa.Text()))
    op.add_column("evidence", sa.Column("plain_language_summary", sa.Text()))


def downgrade() -> None:
    op.drop_column("evidence", "plain_language_summary")
    op.drop_column("evidence", "full_text")
    op.drop_column("evidence", "url")
