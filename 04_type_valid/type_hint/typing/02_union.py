# Python 3.9 이하
# from typing import Union
# def process(value: Union[int, str, float]) -> str:
#     return str(value)

# Python 3.10+
def process(value: str | float) -> str:
    return str(value)
