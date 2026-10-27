import pytest

from streamstats.errors import InvalidEventError, InvalidTimestampError
from streamstats.models import validate_event


def test_validate_valid_event():
    # Проверяем, что валидный словарь превращается в Event с нужными полями
    raw = {"timestamp": "2024-01-15T10:00:00", "level": "ERROR", "source": "db", "message": "x"}
    event = validate_event(raw)
    assert event.level == "ERROR"
    assert event.is_error() is True

def test_validate_missing_field():
    # Проверяем, что отсутствие обязательного поля вызывает InvalidEventError
    raw = {"timestamp": "2024-01-15T10:00:00", "level": "ERROR"}
    with pytest.raises(InvalidEventError):
        validate_event(raw)

def test_validate_bad_timestamp():
    # Проверяем, что кривой формат времени вызывает InvalidTimestampError
    raw = {"timestamp": "вчера", "level": "ERROR", "source": "db", "message": "x"}
    with pytest.raises(InvalidTimestampError):
        validate_event(raw)