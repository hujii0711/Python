# 한 줄씩 읽기 (큰 파일에 적합, 메모리 절약)
with open("06_io/file/data/sample.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())  # strip()으로 끝의 \n 제거
