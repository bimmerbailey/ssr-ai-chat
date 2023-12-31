import structlog.stdlib
from fastapi import Request, Depends
from fastapi.responses import HTMLResponse
from fastapi import APIRouter

from app.routes.ui.template import templates
from app.dependencies.auth import get_current_user

logger = structlog.stdlib.get_logger(__name__)

router = APIRouter(tags=["Dashboard"], dependencies=[Depends(get_current_user)])


@router.get("/dashboard", response_class=HTMLResponse, name="dashboard")
async def get_dashboard(
    request: Request,
):
    return templates.TemplateResponse(
        "views/dashboard.html", context={"request": request}
    )
