# 1. 특정 문자열 치환
with open("06_io/file/data/sample.txt", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("첫 번째", "1번째")

with open("06_io/file/data/sample.txt", "w", encoding="utf-8") as f:
    f.write(text)
