"""
제너레이터 표현식은 "모든 값을 미리 만들 필요 없이, 필요할 때마다 하나씩 계산해서 쓴다"는 개념이 핵심입니다.
대용량 데이터나 무한 시퀀스를 다룰 때 특히 유용합니다.
"""

# 파일이 매우 커도 한 줄씩만 메모리에 올리므로 효율적
with open("huge_file.txt") as f:
    long_lines = (line for line in f if len(line) > 100)
    for line in long_lines:
        print(line)
