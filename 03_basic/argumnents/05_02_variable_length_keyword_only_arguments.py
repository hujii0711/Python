"""
쓰임새를 보여주는 예제로 확장
1. `add_many(korean=90, english=85, math=100)` 처럼 **`이름=값`** 형태로 인자를 넘기면,
2. 함수 내부의 `args`는 자동으로 딕셔너리로 묶입니다:
"""


def add_many(**args):
    print(args)
    result = 0
    for key, value in args.items():
        print(f"{key} = {value}")
        result += value
    return result


a = add_many(korean=90, english=85, math=100)
print(a)
