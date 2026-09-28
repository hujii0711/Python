"""
JSON 문자열 → 딕셔너리 (`loads`)
"""

import json

json_str = '{"법령명": "주택임대차보호법", "MST": 276291}'
data = json.loads(json_str)

print(data)  # {'법령명': '주택임대차보호법', 'MST': 276291}
print(data["법령명"])  # 주택임대차보호법
print(type(data))  # <class 'dict'>
