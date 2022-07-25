from http import HTTPStatus

import aiohttp
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(
            self,
            app,
    ):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        authorization: str = request.headers.get('Authorization')
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'{settings.AUTH_API_HOST}:{settings.AUTH_API_HOST}/{settings.AUTH_API_CHECK_TOKEN_ENDPOINT}',
                    headers={
                        'Authorization': authorization
                    }) as response:
                msg = await response.json()
        if msg.get('message', '').lower() != 'success':
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail='User unauthorized',
            )
        response = await call_next(request)
        return response
