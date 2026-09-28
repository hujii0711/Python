import torch
from sentence_transformers import SentenceTransformer

device = "mps" if torch.backends.mps.is_available() else "cpu"
model = SentenceTransformer("BAAI/bge-m3", device=device)
texts = [
    "파이썬에서 리스트를 뒤집는 방법",
    "list reverse in python",
    "오늘 날씨가 좋네요",
]

embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
print(embeddings.shape)  # (3, 1024)
print([v.tolist() for v in embeddings])
