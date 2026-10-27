import csv
import json

from .errors import InvalidEventError, UnsupportedFormatError


def parse_csv(path):
    """
    Читает CSV-файл построчно и возвращает словари (по одному за раз).
    """
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for line_number, row in enumerate(reader, start=2):
            # 1. Проверяем на пустоту
            if all(v is None or v == "" for v in row.values()):
                continue
            
            # 2. Создаем НОВЫЙ словарь (копию) и добавляем туда номер строки
            new_row = dict(row)
            new_row["_line_num"] = line_number 
            
            # 3. Отдаем новый словарь
            yield new_row

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
                # Тут сразу добавляем номер строки в ошибку
                raise InvalidEventError(f"invalid JSON at line {line_number}")

            if not isinstance(json_dict, dict):
                raise InvalidEventError(f"JSON must be an object at line {line_number}")

            json_dict["_line_num"] = line_number  
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