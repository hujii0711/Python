lst = [1, 2, 3]
gen = (v for v in lst)
enu = enumerate(lst)

for i, a in enu:
    print(i, a)

print("gen:", gen)
