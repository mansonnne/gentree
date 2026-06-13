"""add relationship OTHER type and layout_as column

Revision ID: b2e1f3a7c901
Revises: 4139444aeb74
Create Date: 2026-06-13 00:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = 'b2e1f3a7c901'
down_revision: str | None = '4139444aeb74'
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        'relationships',
        sa.Column('layout_as', sa.String(length=50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('relationships', 'layout_as')
