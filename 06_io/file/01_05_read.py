# 한 줄만 읽기
with open("06_io/file/data/sample.txt", "r", encoding="utf-8") as f:
    first = f.readline()
print(first)
