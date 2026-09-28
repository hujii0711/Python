from typing import Literal

# 특정 값만 허용
Direction = Literal["left", "right", "up", "down"]


def move(direction: Direction) -> None:
    print(f"Moving {direction}")


move("left")  # OK
move("diagonal")  # mypy 오류
