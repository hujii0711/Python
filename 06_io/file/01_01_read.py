"""
with 문을 쓰면 블록이 끝날 때 파일이 자동으로 닫힙니다. open()만 쓰고 close()를 빼먹는 실수를 막아줍니다.
"""

# 전체를 하나의 문자열로 읽기
with open("06_io/file/data/sample.txt", "r", encoding="utf-8") as f:
    content = f.read()
print(content)
