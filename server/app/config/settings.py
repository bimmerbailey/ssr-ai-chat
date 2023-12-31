from functools import lru_cache
from typing import Literal

from llama_index.vector_stores.milvus import DEFAULT_DOC_ID_KEY, DEFAULT_EMBEDDING_KEY
from pydantic import AnyHttpUrl, Field, MongoDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class MongoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="mongo_")
    hostname: str = "mongo"
    port: int = 27017
    password: str = "password"
    name: str = "rag_app"
    username: str = "rag_user"

    url: MongoDsn = f"mongodb://{hostname}:{port}/{name}"


class JwtSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True, env_prefix="jwt_")
    secret_key: str = "secret"
    algorithm: str = "HS256"
    token_expires: int = 60


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(frozen=True)

    url_base: str = "localhost"
    log_level: str = "DEBUG"
    json_logs: bool = False
    fastapi_env: str = "production"
    cookie_name: str = "cookie"

    llm_hf_repo_id: str = "TheBloke/Mistral-7B-Instruct-v0.1-GGUF"
    llm_hf_model_file: str = "mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    embedding_hf_model_name: str = "BAAI/bge-small-en-v1.5"


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="redis_")

    host: str = "redis"
    port: int = 6379
    dsn: RedisDsn = f"redis://{host}:{port}"


class MilvusSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="milvus_")

    uri: AnyHttpUrl = "http://milvus-db"
    hostname: str = str(uri).split("/")[-1]
    collection_name: str = "ragCollection"
    token: str = ""
    dim: int = 384
    embedding_field: str = DEFAULT_EMBEDDING_KEY
    doc_id_field: str = DEFAULT_DOC_ID_KEY
    similarity_metric: str = "IP"
    consistency_level: str = "Strong"
    overwrite: bool = False
    text_key: str | None = None


class S3Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="s3_")

    uri: AnyHttpUrl = "http://minio:9000"
    bucket: str = "a-bucket"
    aws_access_key_id: str = "minioadmin"
    aws_secret_access_key: str = "minioadmin"


class EmbeddingSettings(BaseSettings):
    mode: Literal["local", "openai", "sagemaker", "mock"]
    ingest_mode: Literal["simple", "batch", "parallel"] = Field(
        "simple",
        description=(
            "The ingest mode to use for the embedding engine:\n"
            "If `simple` - ingest files sequentially and one by one. It is the historic behaviour.\n"
            "If `batch` - if multiple files, parse all the files in parallel, "
            "and send them in batch to the embedding model.\n"
            "If `parallel` - parse the files in parallel using multiple cores, and embedd them in parallel.\n"
            "`parallel` is the fastest mode for local setup, as it parallelize IO RW in the index.\n"
            "For modes that leverage parallelization, you can specify the number of "
            "workers to use with `count_workers`.\n"
        ),
    )
    count_workers: int = Field(
        2,
        description=(
            "The number of workers to use for file ingestion.\n"
            "In `batch` mode, this is the number of workers used to parse the files.\n"
            "In `parallel` mode, this is the number of workers used to parse the files and embed them.\n"
            "This is only used if `ingest_mode` is not `simple`.\n"
            "Do not go too high with this number, as it might cause memory issues. (especially in `parallel` mode)\n"
            "Do not set it higher than your number of threads of your CPU."
        ),
    )


mongo_settings = MongoSettings()
jwt_settings = JwtSettings()
app_settings = AppSettings()
redis_settings = RedisSettings()
milvus_settings = MilvusSettings()
s3_settings = S3Settings()


@lru_cache
def get_app_settings() -> AppSettings:
    return AppSettings()


@lru_cache
def get_milvus_settings() -> MilvusSettings:
    return MilvusSettings()


@lru_cache
def get_s3_settings() -> S3Settings:
    return S3Settings()


@lru_cache
def get_redis_settings() -> RedisSettings:
    return RedisSettings()


@lru_cache
def get_jwt_settings() -> JwtSettings:
    return JwtSettings()


@lru_cache
def get_embeddings_settings() -> EmbeddingSettings:
    return EmbeddingSettings(mode="local")
