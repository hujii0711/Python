def title(text: str) -> None:
    print()
    print("-" * 58)
    print(text)
    print("-" * 58)


# ===========================================================================
# 1. 가장 단순한 선언
# ===========================================================================
# def 안에 yield 가 하나라도 있으면 그 함수는 '제너레이터 함수'가 된다.
# return 이 없어도 되고, 몸통에 yield 만 있으면 된다.


def greet():
    yield "안녕"
    yield "반가워"
    yield "잘 가"


def demo_basic() -> None:
    title("1. 선언과 호출")

    print("\n  선언:")
    print("    def greet():")
    print("        yield '안녕'")
    print("        yield '반가워'")
    print("        yield '잘 가'")

    gen = greet()  # <- 호출. 몸통은 아직 한 줄도 실행되지 않는다.
    print(f"\n  호출 결과 : {gen}")
    print(f"  타입      : {type(gen).__name__}")

    print("\n  next() 로 하나씩 꺼낸다 (yield 를 만날 때까지 실행되고 멈춘다):")
    print(f"    next(gen) -> {next(gen)}")
    print(f"    next(gen) -> {next(gen)}")
    print(f"    next(gen) -> {next(gen)}")

    print("\n  더 꺼내면 StopIteration:")
    try:
        next(gen)
    except StopIteration:
        print("    StopIteration  <- 끝났다는 신호")


def main() -> None:
    demo_basic()


if __name__ == "__main__":
    main()
