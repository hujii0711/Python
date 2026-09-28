# 특징 2: 한 번 소진되면 재사용 불가
# 제너레이터는 이터레이터(iterator)이기 때문에, 한 번 순회하고 나면 다시 처음부터 순회할 수 없습니다.
gen = (x for x in range(3))

print(list(gen))  # [0, 1, 2]
print(list(gen))  # [] -> 이미 소진됨!
