"""
`frozenset()` — 수정 불가능한 집합
일반 집합은 수정 가능하지만, `frozenset`은 한 번 만들면 변경할 수 없습니다 (딕셔너리 키나 다른 집합의 원소로 쓸 때 유용).
"""

fs = frozenset([1, 2, 3])
print(fs)  # frozenset({1, 2, 3})
# fs.add(4)  # ❌ 에러 발생! 수정 불가
