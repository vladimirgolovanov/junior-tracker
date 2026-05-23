"""child date of birth and predict enabled

Revision ID: 1f863f624a86
Revises: 3f73de65cab0
Create Date: 2026-05-23 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f863f624a86'
down_revision: Union[str, Sequence[str], None] = '3f73de65cab0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('childs', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('childs', sa.Column('predict_enabled', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('childs', 'predict_enabled')
    op.drop_column('childs', 'date_of_birth')
