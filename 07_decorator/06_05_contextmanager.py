"""
트랜잭션 (성공 시 커밋, 실패 시 롤백)
"""

import sqlite3
from contextlib import contextmanager


@contextmanager
def transaction(conn):
    try:
        yield conn.cursor()
        conn.commit()  # 예외 없이 끝나면 커밋
    except Exception:
        conn.rollback()  # 예외가 나면 롤백
        raise  # 예외는 다시 던지기


conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (name TEXT)")

with transaction(conn) as cur:
    cur.execute("INSERT INTO users VALUES ('철수')")
