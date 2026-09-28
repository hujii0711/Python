from enum import Enum
from typing import Literal

from pydantic import BaseModel


class Role(str, Enum):
    admin = "admin"
    user = "user"


class Account(BaseModel):
    role: Role
    status: Literal["active", "inactive"]


a = Account(role="admin", status="active")
print(a.role)  # Role.admin
