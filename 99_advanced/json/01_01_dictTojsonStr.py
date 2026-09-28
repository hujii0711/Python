"""

핵심 함수 4가지
| 함수            | 방향           | 용도                           |
| -------------- | ------------- | ----------------------------- |
| `json.dumps()` | Python → 문자열 | 파이썬 객체를 JSON 문자열로 변환    |
| `json.dump()`  | Python → 파일  | 파이썬 객체를 JSON 파일로 저장      |
| `json.loads()` | 문자열 → Python | JSON 문자열을 파이썬 객체로 변환    |
| `json.load()`  | 파일 → Python  | JSON 파일을 읽어서 파이썬 객체로 변환 |

딕셔너리 → JSON 문자열 (`dumps`)

Python ↔ JSON 타입 대응표
|Python          |JSON            |
|----------------|----------------|
|`dict`          |`object` `{}`   |
|`list`, `tuple` |`array` `[]`    |
|`str`           |`string`        |
|`int`, `float`  |`number`        |
|`True` / `False`|`true` / `false`|
|`None`          |`null`          |
"""

import json

# <class 'dict'>
data = {"법령명": "주택임대차보호법", "MST": 276291, "현행여부": True, "관련법령": None}

# 딕셔너리 → JSON 문자열 (`dumps`)
json_str = json.dumps(data)
print(json_str)
# {"\ubc95\ub839\uba85": "\uc8fc\ud0dd..."}  ← 한글이 유니코드로 escape됨
# 타입 확인 및 출력 print(type(json_str)) # 결과: <class 'str'>
