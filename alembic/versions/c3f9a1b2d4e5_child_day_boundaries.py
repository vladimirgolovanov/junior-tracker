"""Child day boundaries

Revision ID: c3f9a1b2d4e5
Revises: 51cd432c0aa9
Create Date: 2026-09-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3f9a1b2d4e5'
down_revision: Union[str, Sequence[str], None] = '51cd432c0aa9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('childs', sa.Column('day_start', sa.Time(), nullable=True))
    op.add_column('childs', sa.Column('day_end', sa.Time(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('childs', 'day_end')
    op.drop_column('childs', 'day_start')
