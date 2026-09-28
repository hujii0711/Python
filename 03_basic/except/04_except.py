"""
else, finally
"""

try:
    f = open("data.txt", "r", encoding="utf-8")
except FileNotFoundError:
    print("파일이 없습니다")
else:
    # 예외가 발생하지 않았을 때만 실행
    print(f.read())
    f.close()
finally:
    # 예외 발생 여부와 상관없이 항상 실행 (정리 작업)
    print("처리 종료")
