"""
파일로 저장하기 (`dump`)
"""

import json

# <class 'dict'>
data = {"법령명": "주택임대차보호법", "MST": 276291, "현행여부": True, "관련법령": None}

# 딕셔너리 → JSON 문자열 (`dumps`)
with open("99_advanced/json/data/law_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
