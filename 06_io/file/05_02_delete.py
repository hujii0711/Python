from pathlib import Path

# pathlib 사용 (Python 3.8+)
Path("06_io/file/data/delete.txt").unlink(missing_ok=True)  # 없어도 에러 안 남
