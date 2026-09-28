# 예제 딕셔너리 (과일 재고)
fruit_stock = {"apple": 3, "banana": 5, "cherry": 2}

# 패턴 1: 키(Key)만 순회하기
print("--- 1. 키만 순회 ---")
for fruit in fruit_stock:  # dict.keys()를 사용해도 결과는 같습니다.
    print(f"과일 이름: {fruit}")

print("\n--- 2. 값(Value)만 순회 ---")
# 패턴 2: 값(Value)만 순회하기 (.values() 사용)
for count in fruit_stock.values():
    print(f"재고 수량: {count}")

print("\n--- 3. 키와 값(Key, Value) 동시에 순회 ---")
# 패턴 3: 키와 값을 쌍으로 순회하기 (.items() 사용)
# 딕셔너리 순회에서 가장 많이 쓰이는 방식입니다. (Key, Value) (키와 값의 튜플 쌍)
for fruit, count in fruit_stock.items():
    print(f"{fruit}의 재고는 {count}개 남았습니다.")
