from fastapi import Depends
from sqlalchemy import text, bindparam
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta, datetime

from src import get_db
from src.models import Child


class ChartRepository:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db

    async def get_range_events(
        self,
        child: Child,
        date_from: date,
        date_to: date,
        event_type_ids: tuple[int],
    ):
        query = text("""
                 SELECT event_type_id,
                        (occurred_at AT TIME ZONE :timezone)::timestamp AS occurred_at, description,
                        volume
                 FROM events
                 WHERE (occurred_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone)::date
                      BETWEEN :date_from AND :date_to
                      AND event_type_id IN :event_type_ids
                      AND child_id = :child_id
                 ORDER BY occurred_at
                 """).bindparams(bindparam("event_type_ids", expanding=True))

        results = await self.db.execute(
            query,
            {
                "timezone": child.timezone,
                "date_from": date_from,
                "date_to": date_to,
                "event_type_ids": event_type_ids,
                "child_id": child.id,
            },
        )

        return [dict(row) for row in results.mappings().all()]

    async def get_sleep_events(
        self,
        child_id: int,
        date_from: date,
        date_to: date,
    ):
        query = text("""
                     SELECT child_id, start, "end"
                     FROM sleep_events
                     WHERE child_id = :child_id
                       AND start::date BETWEEN :date_from AND :date_to
                     ORDER BY start
                     """)

        results = await self.db.execute(
            query,
            {
                "child_id": child_id,
                "date_from": date_from,
                "date_to": date_to,
            },
        )

        return [dict(row) for row in results.mappings().all()]

    async def get_sleep_status(self, child_id: int):
        query = text("""
                     SELECT e.occurred_at, et.name AS event_type_name
                     FROM events e
                     JOIN event_types et ON e.event_type_id = et.id
                     WHERE e.child_id = :child_id
                       AND et.name IN ('sleep_start', 'sleep_end')
                     ORDER BY e.occurred_at DESC
                     LIMIT 1
                     """)
        return (await self.db.execute(query, {"child_id": child_id})).mappings().first()

    async def get_last_events_per_type(self, child_id: int):
        query = text("""
                     SELECT DISTINCT ON (e.event_type_id)
                         e.event_type_id,
                         et.name AS event_type_name,
                         et.format,
                         e.occurred_at,
                         e.volume,
                         e.description
                     FROM events e
                     JOIN event_types et ON e.event_type_id = et.id
                     WHERE e.child_id = :child_id
                       AND et.name NOT IN ('sleep_start', 'sleep_end')
                     ORDER BY e.event_type_id, e.occurred_at DESC
                     """)
        results = await self.db.execute(query, {"child_id": child_id})
        return [dict(row) for row in results.mappings().all()]

    async def get_formula_daily(
        self,
        child: Child,
        date_from: date,
        date_to: date,
    ) -> list[dict]:
        query = text("""
            SELECT
                (e.occurred_at AT TIME ZONE :timezone)::date AS day,
                COALESCE(SUM(e.volume), 0)                   AS total_volume,
                COUNT(*)                                     AS count
            FROM events e
            JOIN event_types et ON e.event_type_id = et.id
            WHERE et.name = 'formula'
              AND et.child_id = :child_id
              AND e.child_id = :child_id
              AND (e.occurred_at AT TIME ZONE :timezone)::date BETWEEN :date_from AND :date_to
            GROUP BY day
            ORDER BY day
        """)
        results = await self.db.execute(
            query,
            {
                "timezone": child.timezone,
                "child_id": child.id,
                "date_from": date_from,
                "date_to": date_to,
            },
        )
        return [dict(row) for row in results.mappings().all()]

    async def get_plain_events(self):
        pass

    async def get_cycle_day_events(
        self,
        child: Child,
        cycle_date: date,
        event_type_ids: tuple[int],
    ):
        cycle_date = datetime.combine(cycle_date, datetime.min.time()).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        date_from = cycle_date
        date_to = cycle_date + timedelta(days=1)

        query = text("""
                     SELECT event_type_id,
                            (occurred_at AT TIME ZONE :timezone)::timestamp AS occurred_at, description,
                            volume
                     FROM events
                     WHERE (occurred_at AT TIME ZONE :timezone)::date
                              BETWEEN :date_from AND :date_to
                              AND event_type_id IN :event_type_ids
                              AND child_id = :child_id
                     ORDER BY occurred_at
                     """).bindparams(bindparam("event_type_ids", expanding=True))

        results = await self.db.execute(
            query,
            {
                "timezone": child.timezone,
                "date_from": date_from.date(),
                "date_to": date_to.date(),
                "event_type_ids": event_type_ids,
                "child_id": child.id,
            },
        )

        return [dict(row) for row in results.mappings().all()]
