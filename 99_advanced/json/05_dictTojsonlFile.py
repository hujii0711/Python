"""
JSONL 파일 저장
"""

import json

records = [
    {"id": 1, "text": "첫 번째 청크"},
    {"id": 2, "text": "두 번째 청크"},
]

with open("99_advanced/json/data/chunks.jsonl", "w", encoding="utf-8") as f:
    f.writelines(json.dumps(record, ensure_ascii=False) + "\n" for record in records)
