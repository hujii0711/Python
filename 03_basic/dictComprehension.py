ko_chars = ["가", "나", "다", "라", "마"]

character_to_ids = {}
for i, char in enumerate(ko_chars):
    character_to_ids[char] = i

character_to_ids2 = {char: i for i, char in enumerate(ko_chars)}

print("character_to_ids=====", character_to_ids)
print("character_to_ids2=====", character_to_ids2)
