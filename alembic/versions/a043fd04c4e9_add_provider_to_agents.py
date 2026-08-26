"""add provider to agents

Revision ID: a043fd04c4e9
Revises: 1a528b523d8a
Create Date: 2026-08-22 13:22:23.745118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a043fd04c4e9'
down_revision: Union[str, Sequence[str], None] = '1a528b523d8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'agents',
        sa.Column(
            'provider',
            sa.String(length=50),
            nullable=False,
            server_default='ollama'
        )
    )

    op.alter_column(
        'agents',
        'provider',
        server_default=None
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        'agents',
        'provider'
    )
