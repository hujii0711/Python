"""
가변 위치 인자 (`*args`)
개수 제한 없이 위치 인자들을 튜플로 모아 받습니다.
"""


def add_all(*args):
    print(args)  # 튜플
    return sum(args)


add_all(1, 2, 3, 4)  # (1, 2, 3, 4) -> 10
