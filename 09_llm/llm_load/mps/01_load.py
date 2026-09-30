import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

name = "Qwen2.5-7B-Instruct-4bit"  # "mlx-community/Qwen2.5-7B-Instruct-4bit"  # 양자화 모델은 사용 불가하고 원본 모델 사용 가능 "Qwen/Qwen2.5-1.5B-Instruct"
device = "mps" if torch.backends.mps.is_available() else "cpu"
print(device)  # mps

tokenizer = AutoTokenizer.from_pretrained(name)
model = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float16).to(device)

messages = [{"role": "user", "content": "파이썬 리스트 뒤집는 법 알려줘"}]
inputs = tokenizer.apply_chat_template(
    messages, add_generation_prompt=True, return_tensors="pt", return_dict=True
).to(device)

with torch.no_grad():
    output = model.generate(**inputs, max_new_tokens=200)

# 입력 프롬프트 부분은 잘라내고 새로 생성된 부분만 디코딩
new_tokens = output[0][inputs["input_ids"].shape[1] :]
print(tokenizer.decode(new_tokens, skip_special_tokens=True))
