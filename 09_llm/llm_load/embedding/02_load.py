import torch
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "BAAI/bge-m3",
    device="mps",
    # 메모리와 속도를 더 아끼려면
    model_kwargs={"torch_dtype": torch.float16},
)

texts = [
    "파이썬에서 리스트를 뒤집는 방법",
    "list reverse in python",
    "오늘 날씨가 좋네요",
]

embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
print(embeddings.shape)  # (3, 1024)
