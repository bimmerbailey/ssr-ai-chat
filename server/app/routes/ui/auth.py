from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
import structlog

from app.routes.ui.template import templates

router = APIRouter(tags=["Authentication"])
logger = structlog.stdlib.get_logger(__name__)


@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    return templates.TemplateResponse(
        "views/login.html", context={"request": request}
    )
