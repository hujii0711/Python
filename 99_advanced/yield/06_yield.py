# 기존 방식 (`for` + `yield`)
def sub_generator():
    yield 1
    yield 2


def main_generator():
    # for 문으로 일일이 꺼내서 yield 해야 함
    for value in sub_generator():
        yield value


for item in main_generator():
    print(item)  # 출력: 1, 2


# `yield from` 방식 (간결함)
# `yield from`을 사용하면 `for` 루프 없이 한 줄로 깔끔하게 축약할 수 있습니다.
def new_sub_generator():
    yield 1
    yield 2


def new_main_generator():
    # sub_generator()의 모든 yield를 그대로 전달함
    yield from new_sub_generator()


for item in new_main_generator():
    print(item)  # 출력: 1, 2
