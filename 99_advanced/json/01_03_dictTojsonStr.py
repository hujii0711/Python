import json

# <class 'dict'>
data = {"법령명": "주택임대차보호법", "MST": 276291, "현행여부": True, "관련법령": None}

# 딕셔너리 → JSON 문자열 (`dumps`)
# 보기 좋게 들여쓰기: `indent`
json_str = json.dumps(data, ensure_ascii=False, indent=2)
print(json_str)
