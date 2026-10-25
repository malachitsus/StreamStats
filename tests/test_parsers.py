import pytest
from streamstats.parsers import parse_csv, parse_jsonl
from streamstats.errors import InvalidEventError

# ============ ТЕСТЫ ДЛЯ CSV ======================

def test_parse_csv_valid(tmp_path):
    # tmp_path создает временную папку для теста
    file = tmp_path / "test.csv"
    file.write_text(
        "timestamp,level,source,message\n"
        "2024-01-15,ERROR,db,timeout\n"
        "2024-01-16,INFO,auth,login\n",
        encoding="utf-8"
    )
    
    rows = list(parse_csv(file))
    # Ожидается:
    assert len(rows) == 2 # 2 строки
    assert rows[0]["level"] == "ERROR" # тип события ERROR в нулевой строке
    assert rows[1]["source"] == "auth" # тип источника auth в первой строке

def test_parse_csv_skips_empty_lines(tmp_path):
    file = tmp_path / "test.csv"
    file.write_text(
        "timestamp,level,source,message\n"
        "2024-01-15,ERROR,db,timeout\n"
        "\n"  # пустая строка (должна быть пропущена)
        "2024-01-16,INFO,auth,login\n",
        encoding="utf-8"
    )
    
    rows = list(parse_csv(file))
    assert len(rows) == 2  # Должно остаться только 2 строки, т.к. одну скипнули


# ====================== ТЕСТЫ ДЛЯ JSON =========================

def test_parse_jsonl_valid(tmp_path):
    file = tmp_path / "test.jsonl"
    file.write_text(
        '{"timestamp": "2024-01-15", "level": "ERROR"}\n'
        '{"timestamp": "2024-01-16", "level": "INFO"}\n',
        encoding="utf-8"
    )
    
    rows = list(parse_jsonl(file))
    assert len(rows) == 2
    assert rows[0]["level"] == "ERROR"

def test_parse_jsonl_bad_json(tmp_path):
    file = tmp_path / "test.jsonl"
    file.write_text(
        '{"valid": "json"}\n'
        'это не json\n',
        encoding="utf-8"
    )
    

    with pytest.raises(InvalidEventError) as excinfo:
        list(parse_jsonl(file))
    
    # Проверяем, что в тексте ошибки указан номер строки (2)
    assert "line 2" in str(excinfo.value)