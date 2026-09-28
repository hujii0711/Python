"""
async yield (비동기 제너레이터)
"""

import asyncio


async def async_generator():
    for i in range(5):
        await asyncio.sleep(1)  # 비동기 대기
        yield i  # 값 반환


# 사용
async def main():
    async for value in async_generator():
        print(value)  # 1초마다 0, 1, 2, 3, 4 출력


asyncio.run(main())
