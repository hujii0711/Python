# from typing import Optional

# # 아래 두 표현은 동일 (Python 3.10+는 | 권장)
# def find_user(user_id: int) -> Optional[str]:
#     ...


def find_user(user_id: int) -> str | None:  # 권장
    if user_id == 1:
        return "Alice"
    return None
