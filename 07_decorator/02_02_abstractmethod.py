"""
일반적으로 파이썬에서 "인터페이스"를 만들려면 `abc.ABC`를 상속받아 강제합니다.
→ 이 방식은 명시적 상속(nominal typing)이 필수입니다. `LLM`을 상속하지 않으면 아무리 `generate` 메서드가 있어도 `LLM` 타입으로 인정되지 않습니다.

`Protocol`은 상속 없이도 인정됨 (구조적 타이핑)
→ `MyGPT`, `ClaudeWrapper`는 `LLM`을 전혀 상속받지 않았지만,
`generate(prompt: str) -> str` 메서드 시그니처만 맞으면 타입 체커(mypy 등)가 `LLM` 타입으로 인정합니다.
이걸 "오리가 걷고, 오리처럼 꽥꽥거리면 오리로 취급한다"는 뜻에서 덕 타이핑(duck typing)이라고 부르고,
`Protocol`은 이 덕 타이핑을 타입 힌트 수준에서 공식적으로 지원하는 도구입니다.
"""

from typing import Protocol


class LLM(Protocol):
    def generate(self, prompt: str) -> str: ...


# LLM을 상속받지 않았는데도...
class MyGPT:
    def generate(self, prompt: str) -> str:
        return "응답"


class ClaudeWrapper:
    def generate(self, prompt: str) -> str:
        return "다른 응답"


def call_llm(model: LLM) -> str:
    return model.generate("안녕")


call_llm(MyGPT())  # OK
call_llm(ClaudeWrapper())  # OK
