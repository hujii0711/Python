"""
| 방법                 | 특징                     | 추천 상황                      |
|---------------------|-------------------------|------------------------------|
| Ollama              | 설치, 실행이 가장 쉬움       | 처음 시작할 때, 앱에서 API처럼 호출 |
| MLX-LM              | Apple Silicon 전용, 빠름  | 파이썬 코드로 직접 제어, 파인튜닝    |
| llama-cpp-python    | GGUF 모델 사용, Metal 가속 | GGUF 파일을 직접 다룰 때          |
| transformers (MPS)  | 허깅페이스 표준 방식         | 원본 모델을 그대로 쓰고 싶을 때      |

uv run mlx_lm.generate --model mlx-community/Qwen2.5-7B-Instruct-4bit --prompt "안녕하세요"
uv run mlx_lm.chat --model mlx-community/Qwen2.5-7B-Instruct-4bit
"""

from mlx_lm import generate, load

# 처음 실행할 때 허깅페이스에서 자동 다운로드 (이후에는 캐시 사용)
model, tokenizer = load("mlx-community/Qwen2.5-7B-Instruct-4bit")

messages = [
    {"role": "system", "content": "당신은 친절한 파이썬 코딩 도우미입니다."},
    {"role": "user", "content": "파이썬에서 리스트를 뒤집는 방법을 알려주세요."},
]

# 모델에 맞는 채팅 템플릿 적용 (필수)
prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True)

response = generate(model, tokenizer, prompt=prompt, max_tokens=300, verbose=True)
