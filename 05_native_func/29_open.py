"""
파일을 읽거나 쓰기 위해 여는 함수입니다. 파일 입출력의 시작점이라고 보시면 됩니다.
"""

# 파일 쓰기 (write) - 없으면 새로 생성, 있으면 덮어씀
파일 = open("05_native_func/test.txt", "w", encoding="utf-8")
파일.write("안녕하세요!\n")
파일.write("파이썬 공부 중입니다.")
파일.close()  # 반드시 닫아줘야 함

# 파일 읽기 (read)
파일 = open("05_native_func/test.txt", "r", encoding="utf-8")
내용 = 파일.read()
print(내용)
파일.close()

# 더 안전한 방법: with 구문 사용 (자동으로 close() 해줌)
with open("05_native_func/test.txt", "r", encoding="utf-8") as 파일:
    내용 = 파일.read()
    print(내용)
