"""
유니코드 코드값(정수)을 해당하는 문자로 변환합니다.
"""

print(chr(65))  # 'A'
print(chr(97))  # 'a'
print(chr(44032))  # '가'

# 활용 예: 알파벳 대문자 전체 출력하기
for i in range(65, 91):  # A~Z의 코드값 범위
    print(chr(i), end=" ")
# 결과: A B C D E F G H I J K L M N O P Q R S T U V W X Y Z
