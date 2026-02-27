import re
from datetime import datetime, timedelta
from re import match
from typing import List, Any

from fastapi.params import Depends

from src.repositories.event_type import EventTypeRepository
from src.schemas.event import EventCreateInternal


class TgMsgParser:
    def __init__(self, event_types: list):
        self.event_types = event_types

    def parse_entry(
        self,
        line: str,
        timestamp: datetime,
        child_id: int,
    ) -> list[EventCreateInternal]:
        line = line.strip().lower()
        results = []

        for event_type in self.event_types:
            for keyword in event_type["keywords"]:
                if keyword.lower() in line:
                    match (event_type["type"]):
                        case "range":
                            parsed_lines = self.get_range_events(
                                event_type, keyword, line, timestamp
                            )
                            for parsed_line in parsed_lines:
                                results.append(
                                    EventCreateInternal(
                                        event_type_id=parsed_line["event_type_id"],
                                        occurred_at=parsed_line["occurred_at"],
                                        child_id=child_id,
                                    )
                                )
                        case "metric":
                            parsed_lines = self.get_metric_events(
                                event_type, keyword, line, timestamp
                            )
                            for parsed_line in parsed_lines:
                                results.append(
                                    EventCreateInternal(
                                        event_type_id=parsed_line["event_type_id"],
                                        occurred_at=parsed_line["occurred_at"],
                                        volume=parsed_line["volume"],
                                        child_id=child_id,
                                    )
                                )
                        case "described":
                            parsed_lines = self.get_described_events(
                                event_type, keyword, line, timestamp
                            )
                            for parsed_line in parsed_lines:
                                results.append(
                                    EventCreateInternal(
                                        event_type_id=parsed_line["event_type_id"],
                                        description=parsed_line["description"],
                                        occurred_at=parsed_line["occurred_at"],
                                        child_id=child_id,
                                    )
                                )
                        case "plain":
                            parsed_lines = self.get_plain_events(
                                event_type, keyword, line, timestamp
                            )
                            for parsed_line in parsed_lines:
                                results.append(
                                    EventCreateInternal(
                                        event_type_id=parsed_line["event_type_id"],
                                        occurred_at=parsed_line["occurred_at"],
                                        child_id=child_id,
                                    )
                                )
        return results

    def get_range_events(
        self,
        event_type: dict,
        keyword: str,
        line: str,
        timestamp: datetime,
    ) -> list[dict]:
        results = []
        range_match = re.match(
            r"(?P<start>\d{2}:\d{2})-(?P<end>\d{2}:\d{2})\s+"
            + keyword
            + r"(?:\s*\S+)?",
            line,
            re.IGNORECASE | re.UNICODE,
        )
        if range_match:
            start_time = datetime.strptime(range_match.group("start"), "%H:%M").time()
            end_time = datetime.strptime(range_match.group("end"), "%H:%M").time()
            event_started_at = datetime.combine(timestamp.date(), start_time)
            results.append(
                {
                    "event_type_id": event_type["event_type_id"][0],
                    "occurred_at": event_started_at,
                }
            )
            event_ended_at = datetime.combine(timestamp.date(), end_time)
            if event_ended_at < event_started_at:
                event_ended_at += timedelta(days=1)
            results.append(
                {
                    "event_type_id": event_type["event_type_id"][1],
                    "occurred_at": event_ended_at,
                }
            )

        return results

    def get_metric_events(
        self,
        event_type: dict,
        keyword: str,
        line: str,
        timestamp: datetime,
    ) -> list[dict]:
        results = []
        metric_match = re.match(
            r"(?P<start>\d{2}:\d{2})\s+" + keyword + r"\s+(?P<volume>\d+)(?:\s*\S+)?",
            line,
            re.IGNORECASE | re.UNICODE,
        )
        if metric_match:
            time = datetime.strptime(metric_match.group("start"), "%H:%M").time()
            results.append(
                {
                    "event_type_id": event_type["event_type_id"],
                    "occurred_at": datetime.combine(timestamp.date(), time),
                    "volume": int(metric_match.group("volume")),
                }
            )

        return results

    def get_described_events(
        self,
        event_type: dict,
        keyword: str,
        line: str,
        timestamp: datetime,
    ) -> list[dict]:
        results = []
        described_match = re.match(
            r"(?P<start>\d{2}:\d{2})\s+" + keyword + r"\s+(?P<description>.+)",
            line,
            re.IGNORECASE | re.UNICODE,
        )
        a = repr(line)
        if described_match:
            time = datetime.strptime(described_match.group("start"), "%H:%M").time()
            results.append(
                {
                    "event_type_id": event_type["event_type_id"],
                    "description": described_match.group("description").strip(""),
                    "occurred_at": datetime.combine(timestamp.date(), time),
                }
            )

        return results

    def get_plain_events(
        self,
        event_type: dict,
        keyword: str,
        line: str,
        timestamp: datetime,
    ) -> list[dict]:
        results = []
        plain_match = re.match(
            r"(?P<start>\d{2}:\d{2})\s+" + keyword + r"(?:\s*\S+)?",
            line,
            re.IGNORECASE | re.UNICODE,
        )
        if plain_match:
            time = datetime.strptime(plain_match.group("start"), "%H:%M").time()
            results.append(
                {
                    "event_type_id": event_type["event_type_id"],
                    "occurred_at": datetime.combine(timestamp.date(), time),
                }
            )
        return []
