from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


@dataclass(config=ConfigDict(strict=True))
class User:
    name: str
    age: int


User("철수", "25")  # ValidationError (변환 없이 거부)
