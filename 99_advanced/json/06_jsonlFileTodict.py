"""
JSONL 읽기 (`loads`)
"""

import json

records = []
with open("99_advanced/json/data/chunks.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        records.append(json.loads(line))
print(records)
