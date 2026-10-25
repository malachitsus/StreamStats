
from dataclasses import dataclass
from datetime import datetime

from .errors import InvalidEventError, InvalidTimestampError

ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
ERROR_LEVELS = {"ERROR", "CRITICAL"}

@dataclass(frozen=True)
class Event:
    timestamp: datetime
    level: str
    source: str
    message: str

    def is_error(self):
        return self.level in ERROR_LEVELS

def parse_timestamp(timestamp):
    if not isinstance(timestamp, str) or timestamp == "":
        raise InvalidTimestampError("timestamp is required")

    if timestamp.endswith('Z'):
        timestamp = timestamp.removesuffix("Z") + "+00:00"

    try:
        return datetime.fromisoformat(timestamp)
    except ValueError:
        raise InvalidTimestampError(f"cannot formated from ISO: {timestamp!r}")

def validate_event(raw):
    for field in ["timestamp", "level", "source", "message"]:
        if field not in raw or raw[field] is None:
            raise InvalidEventError(f"missing field: {field!r}")

    ts = parse_timestamp(raw["timestamp"])

    level = raw["level"]
    if level not in ALLOWED_LEVELS:
        raise InvalidEventError(f"invalid level: {level!r}")
    
    source = raw["source"]
    if not isinstance(source, str) or source == '':
        raise InvalidEventError("source must be non-empty string")

    message = raw["message"]
    if not isinstance(message, str):
        raise InvalidEventError("message must be string")

    return Event(ts, level, source, message)