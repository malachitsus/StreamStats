from dataclasses import dataclass
from datetime import datetime

from .constants import ALLOWED_LEVELS, ERROR_LEVELS
from .errors import InvalidEventError, InvalidTimestampError


@dataclass(frozen=True)
class Event:
    """
    Модель события лога.
    """
    timestamp: datetime
    level: str
    source: str
    message: str

    def is_error(self):
        """
        Возвращает True, если уровень события ERROR или CRITICAL.
        """
        return self.level in ERROR_LEVELS

def parse_timestamp(timestamp):
    """
    Парсит строку в формате ISO 8601 в объект datetime.
    """
    if not isinstance(timestamp, str) or timestamp == "":
        raise InvalidTimestampError("timestamp is required")

    if timestamp.endswith('Z'):
        timestamp = timestamp.removesuffix("Z") + "+00:00"

    try:
        return datetime.fromisoformat(timestamp)
    except ValueError:
        raise InvalidTimestampError(f"cannot formated from ISO: {timestamp!r}")

def validate_event(raw):
    """
    Валидирует словарь с данными и возвращает объект Event.
    """
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