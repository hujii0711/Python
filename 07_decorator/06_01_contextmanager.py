"""
with 문에서 쓸 수 있는 컨텍스트 매니저를 클래스 없이 제너레이터 함수 하나로 만들게 해주는 데코레이터입니다. contextlib 모듈에 들어 있습니다.
yield를 기준으로 앞부분은 진입(setup), 뒷부분은 종료(teardown) 때 실행됩니다.
"""

from contextlib import contextmanager


@contextmanager
def my_context():
    print("시작 (setup)")
    yield  # 여기서 with 블록 본문이 실행됨
    print("종료 (teardown)")


with my_context():
    print("본문 실행")

# 시작 (setup)
# 본문 실행
# 종료 (teardown)
