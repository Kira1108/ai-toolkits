from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from functools import lru_cache

@lru_cache(maxsize = None)
def load_model(model_name_or_path: str):
    return SentenceTransformer(model_name_or_path)

class SentenceTransformerEmbedding:
    """Embedding model using Sentence Transformer"""
    def __init__(self, model_name_or_path:str = "BAAI/bge-m3", dim = 1024):
        self.dim = dim
        self.model = load_model(model_name_or_path)
        
    @property
    def dimension(self):
        return self.dim

    def encode(self, texts: str | List[str]) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
        return self.model.encode(texts)

    def encode_batch(self, texts: List[str], batch_size = 20) -> np.ndarray:
        if isinstance(texts, str):
            texts = [texts]
        chunks = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        embeddings = [self.model.encode(chunk) for chunk in chunks]
        return np.vstack(embeddings)