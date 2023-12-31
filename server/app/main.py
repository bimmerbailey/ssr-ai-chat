from contextlib import asynccontextmanager
import pathlib

import structlog.stdlib
from fastapi import FastAPI
from fastapi.routing import Mount
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config.logging import setup_fastapi, setup_logging
from app.config.settings import (
    AppSettings,
    get_app_settings,
)
from app.database.init_db import close_mongo_connection, connect_to_mongo
from app.dependencies.session import RedisClient
from app.routes import (
    auth_ui,
    dashboard_ui,
    chat_ui,
    auth_api,
    users_api,
    upload_api,
    chat_api,
    ingest_api,
)
from app.middleware.session import SessionMiddleware

logger = structlog.stdlib.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_client = await connect_to_mongo()
    red = RedisClient()
    yield
    await close_mongo_connection(db_client)
    await red.close()


current_dir = pathlib.Path(__file__).parent
static_dir = current_dir / "static"


def init_app(app_settings: AppSettings = get_app_settings()):
    setup_logging(
        json_logs=app_settings.json_logs, 
        log_level=app_settings.log_level
    )
    fast_app = FastAPI(
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
        routes=[
            Mount(
                "/static",
                StaticFiles(directory=static_dir),
                name="static",
            )
        ],
    )

    origins = ["*"]

    fast_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    fast_app.add_middleware(
        SessionMiddleware,
        session_cookie=app_settings.cookie_name,
    )
    setup_fastapi(fast_app)
    fast_app.include_router(auth_ui)
    fast_app.include_router(dashboard_ui)
    fast_app.include_router(chat_ui)
    fast_app.include_router(auth_api)
    fast_app.include_router(users_api)
    fast_app.include_router(upload_api)
    fast_app.include_router(ingest_api)
    fast_app.include_router(chat_api)

    return fast_app
