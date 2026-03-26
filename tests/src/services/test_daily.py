import pytest
from datetime import datetime, timezone

from src.services.daily import TimelineService

rows = [
    {"event_type_id": 2, "occurred_at": "2026-03-14 04:50:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-14 06:35:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-14 07:50:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-14 10:35:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-14 11:05:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-14 13:50:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-14 14:35:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-14 14:45:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-14 15:35:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-14 18:45:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 05:45:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 07:35:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 08:15:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 10:35:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 12:05:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 15:10:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 16:15:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 19:00:00.000000"},
    {"event_type_id": 2, "occurred_at": "2026-03-15 22:55:00.000000"},
    {"event_type_id": 1, "occurred_at": "2026-03-15 23:05:00.000000"},
]

# rows = [
#     {
#         "id": 92,
#         "event_type_id": 5,
#         "occured_at": datetime(2026, 3, 14, 0, 5, tzinfo=timezone.utc),
#         "description": None,
#         "volume": 145,
#     },
#     {
#         "id": 93,
#         "event_type_id": 5,
#         "occured_at": datetime(2026, 3, 14, 3, 15, tzinfo=timezone.utc),
#         "description": None,
#         "volume": 135,
#     },
#     {
#         "id": 95,
#         "event_type_id": 2,
#         "occured_at": datetime(2026, 3, 14, 4, 50, tzinfo=timezone.utc),
#         "description": None,
#         "volume": None,
#     },
#     {
#         "id": 96,
#         "event_type_id": 3,
#         "occured_at": datetime(2026, 3, 14, 5, 40, tzinfo=timezone.utc),
#         "description": "овсянка, йогурт, яблоко, хлеб",
#         "volume": None,
#     },
#     {
#         "id": 97,
#         "event_type_id": 4,
#         "occured_at": datetime(2026, 3, 14, 6, 0, tzinfo=timezone.utc),
#         "description": None,
#         "volume": None,
#     },
#     {
#         "id": 99,
#         "event_type_id": 5,
#         "occured_at": datetime(2026, 3, 14, 6, 30, tzinfo=timezone.utc),
#         "description": None,
#         "volume": 100,
#     },
#     {
#         "id": 98,
#         "event_type_id": 1,
#         "occured_at": datetime(2026, 3, 14, 6, 35, tzinfo=timezone.utc),
#         "description": None,
#         "volume": None,
#     },
#     {
#         "id": 100,
#         "event_type_id": 2,
#         "occured_at": datetime(2026, 3, 14, 7, 50, tzinfo=timezone.utc),
#         "description": None,
#         "volume": None,
#     },
#     {
#         "id": 101,
#         "event_type_id": 5,
#         "occured_at": datetime(2026, 3, 14, 9, 50, tzinfo=timezone.utc),
#         "description": None,
#         "volume": 135,
#     },
#     {
#         "id": 102,
#         "event_type_id": 1,
#         "occured_at": datetime(2026, 3, 14, 10, 35, tzinfo=timezone.utc),
#         "description": None,
#         "volume": None,
#     },
#     {
#         "id": 103,
#         "event_type_id": 2,
#         "occured_at": datetime(2026, 3, 14, 11, 5, tzinfo=timezone.utc),
#         "description": None,
#         "volume": None,
#     },
#     {
#         "id": 104,
#         "event_type_id": 5,
#         "occured_at": datetime(2026, 3, 14, 11, 45, tzinfo=timezone.utc),
#         "description": None,
#         "volume": 135,
#     },
#     {
#         "id": 106,
#         "event_type_id": 3,
#         "occured_at": datetime(2026, 3, 14, 12, 10, tzinfo=timezone.utc),
#         "description": "банан",
#         "volume": None,
#     },
#     {
#         "id": 105,
#         "event_type_id": 4,
#         "occured_at": datetime(2026, 3, 14, 12, 30, tzinfo=timezone.utc),
#         "description": None,
#         "volume": None,
#     },
#     {
#         "id": 107,
#         "event_type_id": 3,
#         "occured_at": datetime(2026, 3, 14, 13, 15, tzinfo=timezone.utc),
#         "description": "кукуруза, шпинат, курица, редиска",
#         "volume": None,
#     },
#     {
#         "id": 108,
#         "event_type_id": 1,
#         "occured_at": datetime(2026, 3, 14, 13, 50, tzinfo=timezone.utc),
#         "description": None,
#         "volume": None,
#     },
#     {
#         "id": 109,
#         "event_type_id": 2,
#         "occured_at": datetime(2026, 3, 14, 14, 35, tzinfo=timezone.utc),
#         "description": None,
#         "volume": None,
#     },
#     {
#         "id": 110,
#         "event_type_id": 5,
#         "occured_at": datetime(2026, 3, 14, 14, 45, tzinfo=timezone.utc),
#         "description": None,
#         "volume": 135,
#     },
#     {
#         "id": 111,
#         "event_type_id": 1,
#         "occured_at": datetime(2026, 3, 14, 14, 45, tzinfo=timezone.utc),
#         "description": None,
#         "volume": None,
#     },
#     {
#         "id": 112,
#         "event_type_id": 2,
#         "occured_at": datetime(2026, 3, 14, 15, 35, tzinfo=timezone.utc),
#         "description": None,
#         "volume": None,
#     },
#     {
#         "id": 113,
#         "event_type_id": 5,
#         "occured_at": datetime(2026, 3, 14, 18, 5, tzinfo=timezone.utc),
#         "description": None,
#         "volume": 190,
#     },
#     {
#         "id": 114,
#         "event_type_id": 1,
#         "occured_at": datetime(2026, 3, 14, 18, 45, tzinfo=timezone.utc),
#         "description": None,
#         "volume": None,
#     },
#     {
#         "id": 115,
#         "event_type_id": 5,
#         "occured_at": datetime(2026, 3, 14, 21, 0, tzinfo=timezone.utc),
#         "description": None,
#         "volume": 190,
#     },
#     {
#         "id": 118,
#         "event_type_id": 1,
#         "occured_at": datetime(2026, 3, 14, 23, 5, tzinfo=timezone.utc),
#         "description": None,
#         "volume": None,
#     },
# ]
#


class TestTimelineService:
    def test_build_timeline(self):
        service = TimelineService()
        pairs = service.get_range_events(rows)
        # echo pairs
        print("\n")
        print(*pairs, sep="\n")
