"""
자주 하는 실수

팁
- range(len(x))는 인덱스가 꼭 필요할 때만 쓰고, 값만 필요하면 for item in x, 둘 다 필요하면 enumerate를 쓰세요.
- range는 Python 3에서 지연 평가 객체입니다. Python 2의 xrange와 같은 방식이라 큰 범위도 안전합니다.
- list(range(n))을 만들어 놓고 순회하는 것보다 range(n)을 바로 순회하는 편이 메모리 면에서 낫습니다.
"""

# 1. 끝 값이 포함된다고 착각
print(list(range(1, 5)))  # [1, 2, 3, 4] (5는 없음)

# 2. 실수(float)는 사용 불가
# range(0, 1, 0.1)   -> TypeError
# 실수 간격이 필요하면 컴프리헨션 사용
print([i * 0.1 for i in range(5)])  # [0.0, 0.1, 0.2, 0.30000000000000004, 0.4]
# 정밀한 간격이 필요하면 numpy.arange / numpy.linspace 사용

# 3. 반복 중 리스트 수정
nums = [1, 2, 3, 4]
for i in range(len(nums)):
    nums[i] *= 2  # 값 수정은 OK
# 반복 중 삭제(pop, remove)는 인덱스가 어긋나므로 피하기
