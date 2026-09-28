"""
파일에서 읽기 (`load`)
"""

import json

with open("99_advanced/json/data/law_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(data["법령명"])  # 주택임대차보호법
