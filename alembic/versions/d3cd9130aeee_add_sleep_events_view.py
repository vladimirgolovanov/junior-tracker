"""add_sleep_events_view

Revision ID: d3cd9130aeee
Revises: 56058c6d6eec
Create Date: 2026-03-22 20:33:51.218189

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d3cd9130aeee"
down_revision: Union[str, Sequence[str], None] = "56058c6d6eec"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
CREATE VIEW sleep_events AS
WITH sleep_starts AS (
    SELECT
        e.child_id,
        e.occurred_at AS start_utc,
        et.name
    FROM events e
    JOIN event_types et ON e.event_type_id = et.id
    WHERE et.name = 'sleep_start'
),
sleep_ends AS (
    SELECT
        e.child_id,
        e.occurred_at AS end_utc,
        et.name
    FROM events e
    JOIN event_types et ON e.event_type_id = et.id
    WHERE et.name = 'sleep_end'
),
paired AS (
    SELECT
        s.child_id,
        s.start_utc,
        MIN(e.end_utc) AS end_utc
    FROM sleep_starts s
    JOIN sleep_ends e
        ON e.child_id = s.child_id
        AND e.end_utc > s.start_utc
    GROUP BY s.child_id, s.start_utc
)
SELECT
    p.child_id,
    TO_CHAR(
        p.start_utc AT TIME ZONE c.timezone,
        'YYYY-MM-DD HH24:MI:SS'
    ) AS start,
    TO_CHAR(
        p.end_utc AT TIME ZONE c.timezone,
        'YYYY-MM-DD HH24:MI:SS'
    ) AS end
FROM paired p
JOIN childs c ON c.id = p.child_id
ORDER BY p.child_id, p.start_utc
""")


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS sleep_events")
