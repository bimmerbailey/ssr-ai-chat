# UI routes
from .ui.auth import router as auth_ui
from .ui.dashboard import router as dashboard_ui
from .ui.chat import router as chat_ui

# API routes
from .auth import router as auth_api
from .chat import chat_router as chat_api
from .ingest import router as ingest_api
from .upload import router as upload_api
from .users import router as users_api

__all__ = [
    "auth_ui",
    "dashboard_ui",
    "chat_ui",
    "auth_api",
    "chat_api",
    "ingest_api",
    "upload_api",
    "users_api",
]
