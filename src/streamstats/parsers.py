import csv
import json

from .errors import InvalidEventError, UnsupportedFormatError


def parse_csv(path):
    """
    Читает CSV-файл построчно и возвращает словари (по одному за раз).
    """
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if all(v is None or v == "" for v in row.values()):
                continue
            yield row

def parse_jsonl(path):
    """
    Читает JSONL-файл построчно, парсит каждую строку как JSON и возвращает словари.
    """
    with open(path, encoding="utf-8-sig") as f:
        for line_number, line in enumerate(f, start=1):
            line_clean = line.strip()

            if line_clean == '':
                continue

            try:
                json_dict = json.loads(line_clean)
            except json.JSONDecodeError:
                raise InvalidEventError(f"invalid JSON at line {line_number}")

            if not isinstance(json_dict, dict):
                raise InvalidEventError("JSON must be an object")

            yield json_dict

def get_parsers(format_name):
    """
    Возвращает функцию-парсер (parse_csv или parse_jsonl) в зависимости от формата.
    """
    if format_name == 'csv':
        return parse_csv
    elif format_name == 'jsonl':
        return parse_jsonl
    else:
        raise UnsupportedFormatError(f"unsupported format: {format_name}")