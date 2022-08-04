from core.config import settings

import aiohttp
from fastapi import Request
from fastapi.logger import logger

FIELDS_TO_ORDER = [
    'imdb_rating',
    'title.raw',
    'genres.id'
]


def validate_order_field(field: str):
    reverse = ['-' + item for item in FIELDS_TO_ORDER]
    all_fields = FIELDS_TO_ORDER + reverse
    if all_fields.count(field) > 0:
        return True
    else:
        return False


def parseOrderField(field: str):
    if field[0] == "-":
        return 'desc', field[1:]
    else:
        return 'asc', field


async def token_validation(request: Request) -> bool:
    """
    Метод для проверки валидности токена.
    Обращается за проверкой в Auth API.
    """
    try:
        authorization: str = request.headers.get('Authorization')
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'{settings.AUTH_API_HOST}:{settings.AUTH_API_PORT}{settings.AUTH_API_CHECK_TOKEN_ENDPOINT}',
                    headers={'Authorization': authorization},
            ) as response:
                msg = await response.json()

        if msg.get('message', '').lower() != 'success':
            logger.warn(f'Validation failed: {msg}')
            return False

        return True
    except Exception as e:
        logger.error(f'Something went wrong: {e}')
        return False
