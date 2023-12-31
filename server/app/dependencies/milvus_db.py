from typing import Any, ClassVar, Optional

import structlog.stdlib
from llama_index.vector_stores.milvus import (
    DEFAULT_DOC_ID_KEY,
    DEFAULT_EMBEDDING_KEY,
    MilvusVectorStore,
)
from pymilvus import (
    Collection,
    CollectionSchema,
    DataType,
    FieldSchema,
    MilvusClient,
    utility,
)

from app.config.settings import milvus_settings, s3_settings

logger = structlog.stdlib.get_logger(__name__)


def init_milvus_client() -> MilvusClient:
    logger.info("Connecting to Milvus...", db=milvus_settings.uri)
    vector_store = MilvusVectorStore(
        uri=str(milvus_settings.uri),
        dim=8,
        collection_name=milvus_settings.collection_name,
    )
    logger.info("Connected to Milvus!")
    return vector_store.client


def close_milvus_client(client: MilvusClient):
    logger.info("Closing connection to Milvus...")
    client.close()
    logger.info("Connection closed!")


class MilvusStoreComponent(MilvusVectorStore):
    def __init__(
        self,
        uri: str = str(milvus_settings.uri),
        collection_name: str = milvus_settings.collection_name,
        dim: Optional[int] = 8,
        **kwargs: Any,
    ):
        super().__init__(
            uri=uri,
            collection_name=collection_name,
            dim=dim,
            **kwargs,
        )

    @property
    def client(self) -> MilvusClient:
        return self.milvusclient

    def insert_file(self, file: str):
        logger.debug("Inserting", client=self.client)
        schema = CollectionSchema(
            [
                FieldSchema("film_id", DataType.INT64, is_primary=True),
                FieldSchema("films", dtype=DataType.FLOAT_VECTOR, dim=2),
            ]
        )
        collection = Collection("test_collection_bulk_insert", schema)
        task_id = utility.do_bulk_insert(
            collection_name=collection.name, files=[f"{s3_settings.bucket}/1.txt"]
        )
        logger.debug("Task", id=task_id)
