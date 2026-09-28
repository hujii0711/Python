"""
반복
"""

colors = ["red", "green", "blue"]

for c in colors:
    print(c)

for i, c in enumerate(colors, start=1):
    print(i, c)  # 1 red / 2 green / 3 blue

names = ["철수", "영희"]
scores = [90, 85]
for name, score in zip(names, scores):
    print(name, score)
