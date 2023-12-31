import io
from typing import Iterator

import boto3
import botocore.client
import structlog.stdlib
from mypy_boto3_s3.service_resource import Bucket, S3ServiceResource

from app.config.settings import s3_settings

logger = structlog.stdlib.get_logger(__name__)


def init_s3_client() -> S3ServiceResource:
    logger.info("Connecting to Minio/S3...")
    client = boto3.resource(
        "s3",
        endpoint_url=f"{s3_settings.uri}",
        aws_access_key_id=s3_settings.aws_access_key_id,
        aws_secret_access_key=s3_settings.aws_secret_access_key,
        aws_session_token=None,
        config=botocore.client.Config(signature_version="s3v4"),
        verify=False,
    )
    logger.info("Connected to Minio/S3!")
    return client


class S3Exception(Exception):
    pass


class S3Client:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.connect()
        return cls._instance

    @classmethod
    def connect(cls):
        cls.client: S3ServiceResource = init_s3_client()

    @property
    def bucket(self) -> Bucket:
        return self.client.Bucket(s3_settings.bucket)

    def download(self, file_name: str) -> Iterator[bytes]:
        file = io.BytesIO()
        self.bucket.download_fileobj(file_name, file)
        contents = file.getvalue()
        file.close()
        yield contents
