from datetime import date

from fastapi import HTTPException
from mcp.server.fastmcp import FastMCP
from sqlalchemy import select

from src.db_helper import async_session_maker
from src.mcp.auth import get_current_user
from src.models.child import Child
from src.models.user import User
from src.repositories.chart import ChartRepository
from src.repositories.child import ChildRepository
from src.services.chart import Chart
from src.services.daily import TimelineService

mcp = FastMCP("junior-tracker", streamable_http_path="/")


def _make_chart_service(session) -> Chart:
    return Chart(
        service=TimelineService(),
        chart_repository=ChartRepository(db=session),
        child_repository=ChildRepository(db=session),
    )


@mcp.tool()
async def list_children() -> list[dict]:
    """Return all children accessible to the authenticated user."""
    user = get_current_user()

    async with async_session_maker() as session:
        result = await session.execute(
            select(Child).join(Child.users).where(User.id == user.id)
        )
        children = result.scalars().all()

    return [{"id": c.id, "name": c.name, "timezone": c.timezone} for c in children]


@mcp.tool()
async def get_chart_data(
    child_id: int,
    date_from: str,
    date_to: str,
    event_type_ids: list[int],
) -> list[dict]:
    """
    Return sleep/event range segments for a child over a date range.

    event_type_ids must contain exactly 2 IDs: [start_event_type_id, end_event_type_id].
    Use list_children to find valid child_id values.

    Each returned segment: day (YYYY-MM-DD), start (ISO datetime), end (ISO datetime),
    duration_minutes (int).
    """
    user = get_current_user()
    df = date.fromisoformat(date_from)
    dt = date.fromisoformat(date_to)

    try:
        async with async_session_maker() as session:
            chart = _make_chart_service(session)
            segments = await chart.get_chart_data(
                user=user,
                child_id=child_id,
                date_from=df,
                date_to=dt,
                event_type_ids=event_type_ids,
            )
    except HTTPException as exc:
        raise Exception(exc.detail) from exc

    return [
        {
            "day": seg["day"],
            "start": seg["start"].isoformat(),
            "end": seg["end"].isoformat(),
            "duration_minutes": round(
                (seg["end"] - seg["start"]).total_seconds() / 60
            ),
        }
        for seg in segments
    ]
