from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from api.v1.view_models import FilmShort
from api.v1.view_models import Genre, GenreShort
from models.models import init_from
from services.movie_service import MovieService
from services.service_locator import get_film_service, get_genre_service

router = APIRouter()


@router.get(
    '/{genre_id}',
    response_model=Genre,
    summary="Genre detail",
    description="Provide full info about single genre by ID"
)
async def genre_details(genre_id: str,
                        genre_service: MovieService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genre not found')

    return Genre.parse_obj(genre)


@router.get(
    '/',
    summary="Genre list",
    description="Fetch all genres"
)
async def genre_list(genre_service: MovieService = Depends(get_genre_service)) -> list[GenreShort]:
    genres = await genre_service.uber_get()
    if not genres:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Genres not found')

    return [GenreShort.parse_obj(genre) for genre in genres]


@router.get(
    '/{genre_id}/film/',
    summary="Film by genre ID",
    description="Gets films by given genre"
)
async def film_list(genre_id: Optional[str] = None,
                    page_size: Optional[int] = 50,
                    page_number: Optional[int] = 1,
                    film_service: MovieService = Depends(get_film_service)) -> list[FilmShort]:
    films = await film_service.uber_get(page_size=page_size,
                                        page_number=page_number,
                                        search_value=genre_id,
                                        property_full_path='genres.id'
                                        )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return [FilmShort.parse_obj(film) for film in films]
