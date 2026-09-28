ko_chars = ["안", "녕", "하", "세", "요"]
character_to_ids = {char: i for i, char in enumerate(ko_chars)}
ids_to_character = {i: char for i, char in enumerate(ko_chars)}


print("character_to_ids=====", character_to_ids)
print("ids_to_character=====", ids_to_character)


# 일반 함수 정의
def token_encode(s):
    return [character_to_ids[c] for c in s]


def token_decode(l):
    return "".join([ids_to_character[i] for i in l])


text = "안녕하세요"
encoded = token_encode(text)
decoded = token_decode(encoded)
print("인코딩:", encoded)  # [0, 1, 2, 3, 4]
print("디코딩:", decoded)  # 안녕하세요

# ---

# lambda 함수 활용
text2 = "안녕하세요"
token_encode2 = lambda s: [character_to_ids[c] for c in s]
token_decode2 = lambda l: "".join([ids_to_character[i] for i in l])
encoded_result = token_encode2(text2)

print("인코딩2:", token_encode2(text2))  # [0, 1, 2, 3, 4]
print("디코딩2:", token_decode2(encoded_result))  # 안녕하세요
