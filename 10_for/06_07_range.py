"""
실용 예제
"""

# 1. 리스트를 n개씩 나누기 (청크)
data = list(range(1, 11))
n = 3
chunks = [data[i : i + n] for i in range(0, len(data), n)]
print(chunks)  # [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]]

# 2. 짝수, 홀수 번째 요소
items = ["a", "b", "c", "d", "e"]
print([items[i] for i in range(0, len(items), 2)])  # ['a', 'c', 'e']

# 3. 재시도 횟수 제한
for attempt in range(1, 4):
    print(f"{attempt}번째 시도")

# 4. 카운트다운
for i in range(3, 0, -1):
    print(i)
print("발사!")


# 5. 소수 판별
def is_prime(n):
    if n < 2:
        return False
    return all(n % i != 0 for i in range(2, int(n**0.5) + 1))


print([n for n in range(2, 30) if is_prime(n)])
# [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
