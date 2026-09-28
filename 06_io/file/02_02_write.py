lines = ["사과\n", "바나나\n", "체리\n"]
with open("06_io/file/data/fruits.txt", "w", encoding="utf-8") as f:
    f.writelines(lines)
