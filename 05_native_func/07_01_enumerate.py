"""
반복문에서 순서(인덱스)와 값을 동시에 가져오고 싶을 때 사용합니다. 초보자들이 정말 많이 쓰게 되는 함수예요.
"""

과일 = ["사과", "바나나", "체리"]

# enumerate 없이 하면 이렇게 번거로움
for i in range(len(과일)):
    print(i, 과일[i])

# enumerate로 훨씬 깔끔하게
for i, 이름 in enumerate(과일):
    print(i, 이름)
# 0 사과
# 1 바나나
# 2 체리

# 시작 번호를 1부터 하고 싶을 때
for i, 이름 in enumerate(과일, start=1):
    print(f"{i}번: {이름}")
# 1번: 사과
# 2번: 바나나
# 3번: 체리
