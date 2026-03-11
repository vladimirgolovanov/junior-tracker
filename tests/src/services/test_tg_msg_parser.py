import pytest
from datetime import datetime, timezone

from src.services.tg_msg_parser import TgMsgParser

event_types = [
    {
        "type": "range",
        "event_type_id": (1, 2),
        "keywords": ["сон"],
    },
    {
        "type": "metric",
        "event_type_id": 5,
        "keywords": ["смесь", "смест"],
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


class TestTgMsgParser:

    @pytest.fixture
    def parser(self):
        return TgMsgParser(event_types)

    @pytest.fixture
    def base_date(self):
        return datetime(2025, 2, 22)

    def test_parse_sleep(self, parser, base_date):
        entries = parser.parse_entry(
            "07:45-08:30 сон", base_date, 1, "Europe/London", 1
        )

        assert len(entries) == 2

        assert entries[0].event_type_id == 1
        assert entries[0].occurred_at == datetime(
            2025, 2, 22, 7, 45, tzinfo=timezone.utc
        )

        assert entries[1].event_type_id == 2
        assert entries[1].occurred_at == datetime(
            2025, 2, 22, 8, 30, tzinfo=timezone.utc
        )

    def test_parse_sleep_case_insensitive(self, parser, base_date):
        entries = parser.parse_entry(
            "07:45-08:35 СОН", base_date, 1, "Europe/London", 1
        )
        assert len(entries) == 2
        assert entries[0].event_type_id == 1

    def test_parse_formula(self, parser, base_date):
        entries = parser.parse_entry(
            "03:55 смесь 205", base_date, 1, "Europe/London", 1
        )

        assert len(entries) == 1
        assert entries[0].event_type_id == 5
        assert entries[0].occurred_at == datetime(
            2025, 2, 22, 3, 55, tzinfo=timezone.utc
        )
        assert entries[0].volume == 205

    def test_parse_formula_different_amount_ml(self, parser, base_date):
        entries = parser.parse_entry(
            "14:30 смесь 180 мл", base_date, 1, "Europe/London", 1
        )

        assert entries[0].event_type_id == 5
        assert entries[0].volume == 180
        assert entries[0].occurred_at == datetime(
            2025, 2, 22, 14, 30, tzinfo=timezone.utc
        )

    def test_parse_food(self, parser, base_date):
        entries = parser.parse_entry(
            "10:45 прикорм овсянка банан", base_date, 1, "Europe/London", 1
        )

        assert len(entries) == 1
        assert entries[0].event_type_id == 3
        assert entries[0].occurred_at == datetime(
            2025, 2, 22, 10, 45, tzinfo=timezone.utc
        )
        assert entries[0].description == "овсянка банан"

    def test_parse_food_single_word(self, parser, base_date):
        entries = parser.parse_entry(
            "12:00 прикорм каша", base_date, 1, "Europe/London", 1
        )

        assert entries[0].event_type_id == 3
        assert entries[0].description == "каша"

    def test_parse_food_multiple_words(self, parser, base_date):
        entries = parser.parse_entry(
            "18:30 прикорм пюре кабачок индейка", base_date, 1, "Europe/London", 1
        )

        assert len(entries) == 1
        assert entries[0].event_type_id == 3
        assert entries[0].description == "пюре кабачок индейка"

    def test_parse_empty_string(self, parser, base_date):
        entries = parser.parse_entry("", base_date, 1, "Europe/London", 1)
        assert entries == []

    def test_parse_unknown_format(self, parser, base_date):
        entries = parser.parse_entry("какой-то текст", base_date, 1, "Europe/London", 1)
        assert entries == []

    def test_parse_with_leading_trailing_spaces(self, parser, base_date):
        entries = parser.parse_entry(
            "  07:45-08:30 сон  ", base_date, 1, "Europe/London", 1
        )
        assert len(entries) == 2

    def test_parse_different_date(self, parser):
        timestamp = datetime(2024, 12, 31)
        entries = parser.parse_entry(
            "23:00-23:45 сон", timestamp, 1, "Europe/London", 1
        )

        assert entries[0].occurred_at == datetime(
            2024, 12, 31, 23, 0, tzinfo=timezone.utc
        )
        assert entries[1].occurred_at == datetime(
            2024, 12, 31, 23, 45, tzinfo=timezone.utc
        )

    def test_midnight_sleep(self, parser):
        timestamp = datetime(2024, 12, 31)
        entries = parser.parse_entry(
            "23:00-00:30 сон", timestamp, 1, "Europe/London", 1
        )

        assert entries[0].occurred_at == datetime(
            2024, 12, 31, 23, 0, tzinfo=timezone.utc
        )
        assert entries[1].occurred_at == datetime(
            2025, 1, 1, 0, 30, tzinfo=timezone.utc
        )

    def test_range_only_start(self, parser, base_date):
        entries = parser.parse_entry("07:45-", base_date, 1, "Europe/London", 1)
        assert len(entries) == 1
        assert entries[0].event_type_id == 1
        assert entries[0].occurred_at == datetime(
            2025, 2, 22, 7, 45, tzinfo=timezone.utc
        )

    def test_timezone(self, parser, base_date):
        entries = parser.parse_entry(
            "10:00 смесь 205", base_date, 1, "Europe/Istanbul", 1
        )
        assert entries[0].occurred_at == datetime(
            2025, 2, 22, 7, 0, tzinfo=timezone.utc
        )
