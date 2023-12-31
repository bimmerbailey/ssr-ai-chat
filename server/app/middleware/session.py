import json
import typing
import secrets
from datetime import datetime, UTC, timedelta

import structlog
from jose import jwt, JWTError
from starlette.datastructures import MutableHeaders
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from redis.asyncio import Redis

from app.dependencies.session import init_redis_client, RedisClient
from app.config.settings import jwt_settings


logger = structlog.stdlib.get_logger(__name__)


class SessionMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        session_cookie: str = "session",
        max_age: typing.Optional[int] = 14 * 24 * 60 * 60,  # 14 days, in seconds
        path: str = "/",
        same_site: typing.Literal["lax", "strict", "none"] = "lax",
        https_only: bool = False,
        domain: typing.Optional[str] = None,
        redis: RedisClient = RedisClient(),
        payload_session_key: str = "session_key",
        scope_session_key: str = "scope_session_key",
    ) -> None:
        self.app = app
        self.session_cookie = session_cookie
        self.max_age = max_age
        self.path = path
        self.security_flags = "httponly; samesite=" + same_site
        if https_only:  # Secure flag can be used with HTTPS only
            self.security_flags += "; secure"
        if domain is not None:
            self.security_flags += f"; domain={domain}"
        self.redis = redis.client
        self.payload_session_key = payload_session_key
        self.scope_session_key = scope_session_key

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        logger.debug("App", scope=scope, receive=receive, send=send)
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        initial_session_was_empty = True

        if self.session_cookie in connection.cookies:
            cookie_data = connection.cookies[self.session_cookie]
            try:
                payload = jwt.decode(
                    cookie_data,
                    key=jwt_settings.secret_key,
                    algorithms=[jwt_settings.algorithm],
                )
                logger.debug("JWT decoded", data=payload)

                scope["session"] = payload
                session_key = payload[self.payload_session_key]
                session = await self.redis.get(session_key)
                if session is not None:
                    scope["session"] = json.loads(session)
                else:
                    scope["session"] = {}
                initial_session_was_empty = False
            except JWTError as err:
                scope["session"] = {}
                logger.warning("JWT error", error=str(err))
        else:
            scope["session"] = {}

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                if scope["session"]:
                    logger.debug("session", scope=scope["session"])
                    # We have session data to persist.
                    set_session_key = scope.pop(
                        self.scope_session_key, secrets.token_hex()
                    )
                    await self.redis.set(
                        set_session_key, json.dumps(scope["session"]), self.max_age
                    )
                    now = datetime.now(tz=UTC)
                    new_payload = {
                        self.payload_session_key: set_session_key,
                        "now": int(now.timestamp()),
                        "expires": int(
                            (now + timedelta(seconds=self.max_age)).timestamp()
                        ),
                    }
                    data = jwt.encode(
                        new_payload,
                        jwt_settings.secret_key,
                        algorithm=jwt_settings.algorithm,
                    )

                    headers = MutableHeaders(scope=message)
                    header_value = "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(  # noqa E501
                        session_cookie=self.session_cookie,
                        data=data,
                        path=self.path,
                        max_age=f"Max-Age={self.max_age}; " if self.max_age else "",
                        security_flags=self.security_flags,
                    )
                    headers.append("Set-Cookie", header_value)
                elif not initial_session_was_empty:
                    # The session has been cleared.
                    headers = MutableHeaders(scope=message)
                    header_value = "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(  # noqa E501
                        session_cookie=self.session_cookie,
                        data="null",
                        path=self.path,
                        expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                        security_flags=self.security_flags,
                    )
                    headers.append("Set-Cookie", header_value)
            await send(message)

        await self.app(scope, receive, send_wrapper)
