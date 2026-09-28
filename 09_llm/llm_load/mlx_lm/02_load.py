from mlx_lm import load, stream_generate

model, tokenizer = load("mlx-community/Qwen2.5-7B-Instruct-4bit")
prompt = tokenizer.apply_chat_template(
    [
        {"role": "system", "content": "당신은 친절한 파이썬 코딩 도우미입니다."},
        {"role": "user", "content": "파이썬에서 리스트를 뒤집는 방법을 알려주세요."},
    ],
    add_generation_prompt=True,
)

for chunk in stream_generate(model, tokenizer, prompt, max_tokens=300):
    print(chunk.text, end="", flush=True)
