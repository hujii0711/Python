# 3. 조건에 맞는 줄 삭제 (빈 줄 제거)
with open("06_io/file/data/sample.txt", "r", encoding="utf-8") as f:
    lines = [line for line in f if line.strip()]

with open("06_io/file/data/sample.txt", "w", encoding="utf-8") as f:
    f.writelines(lines)
