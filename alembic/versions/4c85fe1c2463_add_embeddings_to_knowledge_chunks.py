"""add embeddings to knowledge chunks

Revision ID: 4c85fe1c2463
Revises: 084a8c55339a
Create Date: 2026-08-24 16:01:05.775565

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy.vector


# revision identifiers, used by Alembic.
revision: str = "4c85fe1c2463"
down_revision: Union[str, Sequence[str], None] = "084a8c55339a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "knowledge_chunks",
        sa.Column(
            "embedding",
            pgvector.sqlalchemy.vector.VECTOR(dim=384),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "knowledge_chunks",
        "embedding",
    )