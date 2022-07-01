from http import HTTPStatus
from typing import Optional

from api.v1.utility import validate_order_field, FIELDS_TO_ORDER
from api.v1.view_models import Film, FilmShort, FilmMid
from fastapi import APIRouter, Depends, HTTPException
from models.models import init_from
from services.movie_service import MovieService
from services.service_locator import get_film_service

router = APIRouter()


@router.get(
    '/{film_id}',
    response_model=Film,
    summary="Get detail about single film by ID",
    description="Provide full information about single movie"
)
async def film_details(film_id: str, film_service: MovieService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return init_from(Film,film)


@router.get(
    '/',
    summary="List all films with pagination an optional sort and filtering",
    description=f"sort fields are {FIELDS_TO_ORDER} ."
                f"You can filter list by genre ID"
)
async def film_list(sort: Optional[str] = '-imdb_rating',
                    page_size: Optional[int] = 50,
                    page_number: Optional[int] = 1,
                    filter_genre: Optional[str] = None,
                    film_service: MovieService = Depends(get_film_service)) -> list[FilmShort]:
    if not validate_order_field(sort):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='order field not found')

    if filter_genre is not None:
        films = await film_service.uber_get(page_size=page_size,
                                            page_number=page_number,
                                            search_value=filter_genre,
                                            property_full_path='genres.id',
                                            sort_field=sort
                                            )
    else:
        films = await film_service.uber_get(page_size=page_size,
                                            page_number=page_number,
                                            sort_field=sort
                                            )

    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return [init_from(FilmShort, film) for film in films]


@router.get(
    '/search/',
    summary="Full text search movies ",
    description="Search over database,  search fields are description and title"
)
async def film_list(query: Optional[str],
                    page_size: Optional[int] = 50,
                    page_number: Optional[int] = 1,
                    film_service: MovieService = Depends(get_film_service)) -> list[FilmMid]:
    films = await film_service.uber_get(page_size=page_size,
                                        page_number=page_number,
                                        search_value=query,
                                        search_fields=['title', 'description']
                                        )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return [init_from(FilmMid, film) for film in films]
