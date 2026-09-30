"""
Windows에서 Qwen2.5-7B-Instruct 4bit 실행
Windows에서는 mlx-community/...-4bit 모델(Mac 전용)을 쓸 수 없습니다. 대신 transformers + bitsandbytes로 원본 모델을 4bit(NF4)로 로드하는 방식이 가장 간단합니다. NVIDIA GPU가 필요하고 VRAM은 약 6GB 이상이면 됩니다.
"""

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TextStreamer,
)

MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    quantization_config=bnb_config,
    device_map="auto",
)

streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)


def chat(messages, max_new_tokens=512):
    inputs = tokenizer.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=True,
    ).to(model.device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.8,
            repetition_penalty=1.05,
            streamer=streamer,
        )

    new_tokens = output[0][inputs["input_ids"].shape[1] :]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)


if __name__ == "__main__":
    history = [
        {"role": "system", "content": "당신은 친절한 한국어 AI 어시스턴트입니다."}
    ]

    while True:
        user = input("\n사용자: ").strip()
        if user.lower() in {"exit", "quit", "q"}:
            break
        history.append({"role": "user", "content": user})
        print("Qwen: ", end="")
        answer = chat(history)
        history.append({"role": "assistant", "content": answer})
