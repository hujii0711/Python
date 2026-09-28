"""
파일 경로는 Path로 다루면 Windows와 Mac/Linux 차이를 신경 쓰지 않아도 됩니다.
"""

from pathlib import Path

p = Path("06_io/file/data/sample2.txt")

p.write_text("안녕하세요\n반갑습니다\n", encoding="utf-8")  # 쓰기 (덮어쓰기)
print(p.read_text(encoding="utf-8"))  # 읽기

# 추가 쓰기는 open 사용
with p.open("a", encoding="utf-8") as f:
    f.write("추가된 줄\n")
