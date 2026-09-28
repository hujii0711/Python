# 2. 특정 줄만 수정 (두 번째 줄 변경)
with open("06_io/file/data/sample.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

lines[1] = "수정된 두 번째 줄\n"

with open("06_io/file/data/sample.txt", "w", encoding="utf-8") as f:
    f.writelines(lines)
