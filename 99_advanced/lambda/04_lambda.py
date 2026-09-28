import json

samples = {
    "system_prompt": "당신은 친절한 파이썬 코딩 도우미입니다.",
    "instruction": "파이썬에서 리스트를 뒤집는 방법을 알려주세요.",
    "output": "파이썬에서 리스트를 뒤집으려면 `my_list.reverse()`를 사용하거나 슬라이싱 `my_list[::-1]`을 사용할 수 있습니다.",
}


def transform_sample(sample):
    return {
        "messages": [
            {"role": "system", "content": sample["system_prompt"]},
            {"role": "user", "content": sample["instruction"]},
            {"role": "assistant", "content": sample["output"]},
        ]
    }


train_dataset = map(transform_sample, [samples])

pretty_json = json.dumps(list(train_dataset), indent=4, ensure_ascii=False)

print(pretty_json)

# ---

samples2 = {
    "system_prompt": "당신은 친절한 파이썬 코딩 도우미입니다.",
    "instruction": "파이썬에서 리스트를 뒤집는 방법을 알려주세요.",
    "output": "파이썬에서 리스트를 뒤집으려면 `my_list.reverse()`를 사용하거나 슬라이싱 `my_list[::-1]`을 사용할 수 있습니다.",
}

# ---

train_dataset2 = list(  # noqa: C417
    map(
        lambda s: {
            "messages": [
                {"role": "system", "content": s["system_prompt"]},
                {"role": "user", "content": s["instruction"]},
                {"role": "assistant", "content": s["output"]},
            ]
        },
        [samples2],  # 데이터를 두 번째 인자로 전달
    )
)
pretty_json2 = json.dumps(list(train_dataset2), indent=4, ensure_ascii=False)

print(pretty_json2)

# ---
train_dataset3 = [
    {
        "messages": [
            {"role": "system", "content": s["system_prompt"]},
            {"role": "user", "content": s["instruction"]},
            {"role": "assistant", "content": s["output"]},
        ]
    }
    for s in [samples2]
]
pretty_json3 = json.dumps(list(train_dataset3), indent=4, ensure_ascii=False)

print(pretty_json3)
