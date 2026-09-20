from __future__ import annotations

import hashlib
import math
import re
from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        raise NotImplementedError

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(text) for text in texts]


class HashEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int = 256) -> None:
        if dimension < 2:
            raise ValueError("dimension must be at least 2.")
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Text cannot be empty.")

        tokens = re.findall(r"\b\w+\b", text.lower())
        vector = [0.0] * self.dimension

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector

        return [value / norm for value in vector]
