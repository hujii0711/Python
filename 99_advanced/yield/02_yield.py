def generator():
    print("1번 시작")
    yield 10  # ① 반환 후 일시정지
    print("2번 시작")
    yield 20  # ② 반환 후 일시정지
    print("3번 시작")
    yield 30  # ③ 반환 후 일시정지
    print("끝")


gen = generator()  # 아직 실행 안 됨!

print(next(gen))  # "1번 시작" 출력 → 10 반환
print(next(gen))  # "2번 시작" 출력 → 20 반환
print(next(gen))  # "3번 시작" 출력 → 30 반환
# next(gen)           # StopIteration 예외 발생
