"""
중첩 모델
"""

from pydantic import BaseModel


class Address(BaseModel):
    city: str
    zipcode: str


class Person(BaseModel):
    name: str
    address: Address
    friends: list[str] = []


p = Person.model_validate(
    {
        "name": "철수",
        "address": {"city": "서울", "zipcode": "12345"},
    }
)
print(p.address.city)  # 서울
print(p.model_dump())
# {'name': '철수', 'address': {'city': '서울', 'zipcode': '12345'}, 'friends': []}
