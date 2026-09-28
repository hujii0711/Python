"""
실무에서 많이 사용하는 형태
"""


class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

    def __repr__(self):
        return f"User(id={self.id}, name={self.name!r}, email={self.email!r})"


users = [User(1, "Kim", "kim@test.com"), User(2, "Lee", "lee@test.com")]

print(users)
