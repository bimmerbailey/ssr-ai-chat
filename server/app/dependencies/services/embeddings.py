from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field

from app.dependencies.components.embedding import EmbeddingComponent


class Embedding(BaseModel):
    index: int
    object: Literal["embedding"]
    embedding: list[float] = Field(examples=[[0.0023064255, -0.009327292]])


class EmbeddingsService:
    def __init__(self, embedding_component: EmbeddingComponent) -> None:
        self.embedding_model = embedding_component.embedding_model

    def texts_embeddings(self, texts: list[str]) -> list[Embedding]:
        texts_embeddings = self.embedding_model.get_text_embedding_batch(texts)
        return [
            Embedding(
                index=texts_embeddings.index(embedding),
                object="embedding",
                embedding=embedding,
            )
            for embedding in texts_embeddings
        ]


@lru_cache
def get_embedding_service() -> EmbeddingsService:
    return EmbeddingsService()
