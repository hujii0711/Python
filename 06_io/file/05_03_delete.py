from pathlib import Path

p = Path("06_io/file/data/delete.txt")
print(p.exists())  # 존재 여부
print(p.is_file())  # 파일인지

try:
    with open("no_file.txt", "r", encoding="utf-8") as f:
        print(f.read())
except FileNotFoundError:
    print("파일이 없습니다")
except PermissionError:
    print("권한이 없습니다")
