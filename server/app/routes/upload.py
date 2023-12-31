from typing import Annotated

import structlog.stdlib
from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import StreamingResponse

from app.dependencies.file_storage import S3Client

router = APIRouter(prefix="/api/v1/files", tags=["Files"])
logger = structlog.stdlib.get_logger(__name__)


@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload_files(file: UploadFile, s3_client: Annotated[S3Client, Depends()]):
    s3_client.bucket.upload_fileobj(file.file, file.filename)


@router.get("/")
async def get_files(s3_client: Annotated[S3Client, Depends()]):
    return {"files": [i.key for i in s3_client.bucket.objects.all()]}


@router.get("/download/{file_name}", response_class=StreamingResponse)
async def download_file(file_name: str, s3_client: Annotated[S3Client, Depends()]):
    return StreamingResponse(
        s3_client.download(file_name),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_name}"},
    )
