# 특징 1: 메모리 효율성
# 큰 데이터를 다룰 때 리스트 컴프리헨션은 모든 값을 메모리에 올리지만, 제너레이터는 값을 하나씩만 만들어서 메모리를 훨씬 적게 사용합니다.
import sys

list_comp = [x for x in range(1000000)]
gen_exp = (x for x in range(1000000))

print(sys.getsizeof(list_comp))  # 매우 큼 (수 MB)
print(sys.getsizeof(gen_exp))  # 매우 작음 (약 200바이트 정도)
