# 4. 맨 앞에 내용 추가
with open("06_io/file/data/sample.txt", "r", encoding="utf-8") as f:
    old = f.read()

with open("06_io/file/data/sample.txt", "w", encoding="utf-8") as f:
    f.write("맨 앞에 추가\n" + old)
