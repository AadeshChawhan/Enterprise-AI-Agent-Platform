"""enable pgvector extension

Revision ID: 084a8c55339a
Revises: 4756aaf5776d
Create Date: 2026-08-24 15:32:26.935936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '084a8c55339a'
down_revision: Union[str, Sequence[str], None] = '4756aaf5776d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enable pgvector."""
    op.execute(
        "CREATE EXTENSION IF NOT EXISTS vector"
    )


def downgrade() -> None:
    """Disable pgvector."""
    op.execute(
        "DROP EXTENSION IF EXISTS vector"
    )
