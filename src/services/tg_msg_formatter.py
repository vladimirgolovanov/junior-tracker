from zoneinfo import ZoneInfo


class TgMsgFormatter:
    def __init__(self, event_types: list, tz: str = None):
        self.tz = tz
        self.event_types = event_types

    def set_event_types(self, event_types: list):
        self.event_types = event_types

    def format(self, event, end_event=None) -> str | None:
        event_type = self.find_event_type(event)
        match event_type["type"]:
            case "range":
                if end_event:
                    return f"{event['occurred_at'].astimezone(ZoneInfo(self.tz)).strftime('%H:%M')}-{end_event['occurred_at'].astimezone(ZoneInfo(self.tz)).strftime('%H:%M')} {event_type['keywords'][0]}"
                else:
                    return f"{event['occurred_at'].astimezone(ZoneInfo(self.tz)).strftime('%H:%M')}-"
            case "metric":
                return f"{event['occurred_at'].astimezone(ZoneInfo(self.tz)).strftime('%H:%M')} {event_type['keywords'][0]} {event['volume']}"
            case "described":
                return f"{event['occurred_at'].astimezone(ZoneInfo(self.tz)).strftime('%H:%M')} {event_type['keywords'][0]} {event['description']}"
            case "plain":
                return f"{event['occurred_at'].astimezone(ZoneInfo(self.tz)).strftime('%H:%M')} {event_type['keywords'][0]}"
        return None

    def find_event_type(self, event):
        for et in self.event_types:
            type_id = et["event_type_id"]
            if isinstance(type_id, tuple):
                if event["event_type_id"] in type_id:
                    return et
            else:
                if type_id == event["event_type_id"]:
                    return et
        return None
