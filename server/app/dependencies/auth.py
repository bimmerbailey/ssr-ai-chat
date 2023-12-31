from datetime import datetime, timedelta
from typing import Annotated, Optional

import structlog.stdlib
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt

from app.config.settings import jwt_settings
from app.crud.users import user as user_crud
from app.dependencies.session import SessionAuth
from app.models.users import Users

oauth2_scheme = SessionAuth(token_url="/api/login")

SECRET_KEY = jwt_settings.secret_key
ALGORITHM = jwt_settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = jwt_settings.token_expires

logger = structlog.stdlib.get_logger(__name__)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(
    token: Annotated[Optional[str], Depends(oauth2_scheme)],
):
    return await user_crud.get_one(token)


def get_current_active_user(
    current_user: Users = Depends(get_current_user),
) -> Users:
    if not user_crud.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: Users = Depends(get_current_user),
) -> Users:
    if not user_crud.is_admin(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
