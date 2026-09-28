# 모든 줄을 리스트로 읽기
with open("06_io/file/data/sample.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
print(lines)  # ['첫 번째 줄\n', '두 번째 줄\n', '세 번째 줄\n']
