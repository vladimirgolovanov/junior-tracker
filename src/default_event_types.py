from typing import TypedDict


class RangeEndTemplate(TypedDict):
    name: str
    keywords: list[str] | None
    color: str | None


class EventTypeTemplate(TypedDict):
    name: str
    keywords: list[str] | None
    format: str  # "range" | "metric" | "described" | "plain"
    color: str | None
    range_end: RangeEndTemplate | None  # only for format="range"


DEFAULT_EVENT_TYPES: list[EventTypeTemplate] = [
    {
        "name": "sleep_start",
        "keywords": ["сон"],
        "format": "range",
        "range_end": {
            "name": "sleep_end",
        },
    },
    {
        "name": "formula",
        "keywords": ["смесь"],
        "format": "metric",
        "color": "#ff9eb5",
        "range_end": None,
    },
    {
        "name": "breastfeeding",
        "keywords": ["гв"],
        "format": "described",
        "color": "#2ecc71",
        "range_end": None,
    },
]
