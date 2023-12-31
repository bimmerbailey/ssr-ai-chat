import asyncio
import io
from datetime import datetime, timezone

import structlog
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.config.settings import mongo_settings
from app.dependencies.crypt import hash_password
from app.models.users import Users

logger: structlog.stdlib.BoundLogger = structlog.getLogger(__name__)


async def connect_db():
    kwargs = {
        "username": mongo_settings.username,
        "password": mongo_settings.password,
    }
    client = AsyncIOMotorClient(str(mongo_settings.url), **kwargs)
    await init_beanie(client[mongo_settings.name], document_models=[Users])


async def create_users():
    logger.info("Dropping local Users collection")
    await Users.delete_all()

    users = [
        Users(
            **{
                "email": "admin@your-app.com",
                "first_name": "admin",
                "password": hash_password("password"),
                "created_date": datetime.now(tz=timezone.utc),
                "is_admin": True,
            }
        ),
        Users(
            **{
                "email": "user@your-app.com",
                "first_name": "user",
                "password": hash_password("password"),
                "created_date": datetime.now(tz=timezone.utc),
            }
        ),
    ]

    await Users.insert_many(users)
    logger.info("Users added")


async def create_dev_data():
    await connect_db()
    await create_users()


if __name__ == "__main__":
    asyncio.run(create_dev_data())
