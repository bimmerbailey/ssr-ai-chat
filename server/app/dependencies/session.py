from typing import Annotated

import structlog
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import RedisDsn
from redis.asyncio import Redis

from app.config.settings import (
    RedisSettings,
    app_settings,
    get_redis_settings,
    redis_settings,
)

logger = structlog.stdlib.get_logger(__name__)


class SessionAuth(OAuth2PasswordBearer):
    def __init__(self, token_url: str):
        super().__init__(tokenUrl=token_url)

    async def __call__(self, request: Request) -> str | None:
        logger.info(f"Session", session=request.session)
        authorization = request.session.get("user_id", None)
        if authorization is None:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                )
            else:
                return None
        logger.info(f"Token", token=authorization)
        return authorization


def init_redis_client(url: RedisDsn = redis_settings.dsn) -> Redis:
    logger.info("Connecting to Redis...", db=url)
    client = Redis.from_url(str(url))
    logger.info("Connected to Redis!")
    return client


async def close_redis_client(client: Redis):
    logger.info("Closing connection to Redis...")
    await client.close()
    logger.info("Connection closed!")


class RedisClient:
    _client: Redis

    def __init__(self, settings: RedisSettings = get_redis_settings()):
        self._client = Redis.from_url(str(settings.dsn))
        logger.info("Connected to Redis!")

    async def close(self):
        logger.info("Closing connection to Redis...")
        await self._client.aclose()
        logger.info("Connection closed!")

    def __call__(self) -> Redis:
        return self.client

    @property
    def client(self):
        return self._client
