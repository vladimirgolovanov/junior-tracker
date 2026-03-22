from enum import Enum


class EventTypeName(str, Enum):
    sleep_start = "sleep_start"
    sleep_end = "sleep_end"
