"""
yield로 값 넘기기 (as)
yield한 값이 with ... as 변수에 들어갑니다.
"""

from contextlib import contextmanager


@contextmanager
def open_file(path, mode="r"):
    f = open(path, mode, encoding="utf-8")
    try:
        yield f  # 파일 객체를 with 블록에 전달
    finally:
        f.close()  # 예외가 나도 반드시 닫힘


with open_file("sample.txt", "w") as f:
    f.write("안녕하세요")
