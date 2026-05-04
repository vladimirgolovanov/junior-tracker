from datetime import datetime

import pytest

from src.services.tg_msg_formatter import TgMsgFormatter

event_types = [
    {
        "type": "range",
        "event_type_id": (1, 2),
        "keywords": ["сон"],
    },
    {
        "type": "metric",
        "event_type_id": 5,
        "keywords": ["смесь"],
    },
    {
        "type": "described",
        "event_type_id": 3,
        "keywords": ["прикорм"],
    },
    {
        "type": "plain",
        "event_type_id": 4,
        "keywords": ["покакал"],
    },
]


class TestTgMsgFormatter:
    @pytest.fixture
    def formatter(self):
        return TgMsgFormatter(event_types, "Europe/London")

    def test_format_metric(self, formatter):
        event = {
            "event_type_id": 5,
            "volume": 180,
            "occurred_at": datetime.fromisoformat("2025-02-22T14:30:00.000000+00:00"),
            "description": None,
        }
        assert formatter.format(event) == "14:30 смесь 180"

    def test_format_described(self, formatter):
        event = {
            "event_type_id": 3,
            "occurred_at": datetime.fromisoformat("2025-02-22T14:30:00.000000+00:00"),
            "description": "морковь",
        }
        assert formatter.format(event) == "14:30 прикорм морковь"

    def test_format_plain(self, formatter):
        event = {
            "event_type_id": 4,
            "occurred_at": datetime.fromisoformat("2025-02-22T14:30:00.000000+00:00"),
            "description": None,
        }
        assert formatter.format(event) == "14:30 покакал"

    def test_format_range(self, formatter):
        event = {
            "event_type_id": 1,
            "occurred_at": datetime.fromisoformat("2025-02-22T14:30:00.000000+00:00"),
        }
        assert formatter.format(event) == "14:30-"
        end_event = {
            "event_type_id": 2,
            "occurred_at": datetime.fromisoformat("2025-02-22T15:00:00.000000+00:00"),
        }
        assert formatter.format(event, end_event) == "14:30-15:00 сон"
