"""
가변 키워드 인자 (`**kwargs`)
개수 제한 없이 키워드 인자들을 딕셔너리로 모아 받습니다.
"""


def show_info(**kwargs):
    print(kwargs)  # 딕셔너리


show_info(name="철수", age=20, city="서울")
# {'name': '철수', 'age': 20, 'city': '서울'}
