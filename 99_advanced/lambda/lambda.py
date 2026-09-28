ko_chars = ["가", "나", "다", "라", "마"]
character_to_ids = {char: i for i, char in enumerate(ko_chars)}
ids_to_character = {i: char for i, char in enumerate(ko_chars)}


print("character_to_ids=====", character_to_ids)
print("ids_to_character=====", ids_to_character)

# def token_encode(s):
#     result = []
#     for c in s:
#         result.append(character_to_ids[c])
#     return result

# lambda 매개변수: 표현식
# 결과값은 표현식을 계산한 값이 자동으로 반환됩니다 (return 키워드 불필요).

# # 일반 함수
# def add(x, y):
#     return x + y

# # 람다 함수
# add_lambda = lambda x, y: x + y

# print(add(3, 5))         # 8
# print(add_lambda(3, 5))  # 8

# def token_encode(s):
#     result = []
#     for c in s:
#         result.append(character_to_ids[c])
#     return result


# def token_decode(l):
#     result = []
#     for i in l:
#         result.append(ids_to_character[i])
#     return "".join(result)

token_encode = lambda s: [character_to_ids[c] for c in s]
token_decode = lambda l: "".join([ids_to_character[i] for i in l])
print("token_encode=====", token_encode)
print("token_decode=====", token_decode)

# print(token_encode("안녕하세요 함께 인공지능을 공부하게 되어 반가워요."))
# print(token_decode(token_encode("안녕하세요 함께 인공지능을 공부하게 되어 반가워요.")))
