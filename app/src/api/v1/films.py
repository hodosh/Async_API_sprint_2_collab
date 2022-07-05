from http import HTTPStatus
from typing import Optional

from api.v1.utility import validate_order_field, FIELDS_TO_ORDER
from api.v1.pagination_shema import PaginationSchema
from api.v1.view_models import Film, FilmShort, FilmMid
from fastapi import APIRouter, Depends, HTTPException
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

    return Film.parse_obj(film)

@router.get(
    '/',
    summary="List all films with pagination an optional sort and filtering",
    description=f"sort fields are {FIELDS_TO_ORDER} ."
                f"You can filter list by genre ID"
)
async def film_list(sort: Optional[str] = '-imdb_rating',
                    pagination: PaginationSchema = Depends(),
                    filter_genre: Optional[str] = None,
                    film_service: MovieService = Depends(get_film_service)) -> list[FilmShort]:
    if not validate_order_field(sort):
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='order field not found')

    if filter_genre is not None:
        films = await film_service.uber_get(pagination=pagination,
                                            search_value=pagination.filter_genre,
                                            property_full_path='genres.id',
                                            sort_field=sort
                                            )
    else:
        films = await film_service.uber_get(pagination=pagination,
                                            sort_field=sort
                                            )

    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return [Film.parse_obj(film) for film in films]


@router.get(
    '/search/',
    summary="Full text search movies ",
    description="Search over database,  search fields are description and title"
)
async def film_list(query: Optional[str],
                    pagination: PaginationSchema = Depends(),
                    film_service: MovieService = Depends(get_film_service)) -> list[FilmMid]:
    films = await film_service.uber_get(pagination=pagination,
                                        search_value=query,
                                        search_fields=['title', 'description']
                                        )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return [Film.parse_obj(film) for film in films]
