"""
실행 시간 측정
"""

import time
from contextlib import contextmanager


@contextmanager
def timer(label="작업"):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"{label}: {elapsed:.3f}초")


with timer("합계 계산"):
    sum(range(10_000_000))
# 합계 계산: 0.150초
