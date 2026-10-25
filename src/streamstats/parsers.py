import csv
import json
from .errors import InvalidEventError, UnsupportedFormatError

def parse_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if all(v is None or v == "" for v in row.values()):
                continue
            yield row

