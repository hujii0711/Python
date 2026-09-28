# 줄바꿈 없이 리스트로
with open("06_io/file/data/sample.txt", "r", encoding="utf-8") as f:
    lines = f.read().splitlines()
print(lines)
