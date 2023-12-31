import structlog
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.settings import mongo_settings
from app.models.users import Users

logger = structlog.stdlib.get_logger(__name__)


async def connect_to_mongo() -> AsyncIOMotorClient:
    logger.info("Connecting to MongoDB...")
    kwargs = {
        "username": mongo_settings.username,
        "password": mongo_settings.password,
    }
    client = AsyncIOMotorClient(str(mongo_settings.url), **kwargs)
    await init_beanie(database=client[mongo_settings.name], document_models=[Users])
    logger.info("Connected to MongoDB!")
    return client


async def close_mongo_connection(client: AsyncIOMotorClient):
    logger.info("Closing connection to MongoDB...")
    client.close()
    logger.info("Connection closed!")
