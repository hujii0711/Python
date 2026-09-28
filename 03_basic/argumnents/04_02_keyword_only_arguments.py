"""
별표(*)를 사용하는 방법 (가장 흔함)
* 기호 뒤에 선언된 인자들은 반드시 키워드로만 전달해야 합니다.
"""


def user_info(name, *, age, city):
    print(f"이름: {name}, 나이: {age}, 도시: {city}")


# 1. 올바른 호출 (키워드 명시)
user_info("김철수", age=25, city="서울")

# 2. 에러가 발생하는 호출 (위치 인자로 전달 시)
# user_info("김철수", 25, "서울")  # TypeError 발생!
