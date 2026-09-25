"""Child predict_enabled

Revision ID: e7a2c4d9b1f0
Revises: c3f9a1b2d4e5
Create Date: 2026-09-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7a2c4d9b1f0'
down_revision: Union[str, Sequence[str], None] = 'c3f9a1b2d4e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'childs',
        sa.Column(
            'predict_enabled',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('childs', 'predict_enabled')
