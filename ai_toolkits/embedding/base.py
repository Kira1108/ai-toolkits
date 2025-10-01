from typing import Protocol
import numpy as np

class EmbeddingModel(Protocol):
    """
    Protocol for embedding models.
    """
    
    @property
    def dimension(self) -> int:
        ...
    
    def encode(self, texts: str | list[str]) -> 'np.ndarray':
        ...
    
    def encode_batch(self, texts: list[str], batch_size: int = 20) -> 'np.ndarray':
        ...