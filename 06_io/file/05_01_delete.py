import os

# os 사용
if os.path.exists("06_io/file/data/delete.txt"):
    os.remove("06_io/file/data/delete.txt")

# 폴더 삭제
os.rmdir("empty_dir")  # 빈 폴더만 삭제 가능

import shutil

shutil.rmtree("some_dir")  # 내용이 있는 폴더째 삭제 (복구 불가, 주의)
