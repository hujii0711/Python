import json

# <class 'dict'>
data = {"법령명": "주택임대차보호법", "MST": 276291, "현행여부": True, "관련법령": None}

# 딕셔너리 → JSON 문자열 (`dumps`)
# 한글 깨짐(유니코드 escape) 방지: `ensure_ascii=False`
json_str = json.dumps(data, ensure_ascii=False)
print(json_str)
