from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from api.v1.pagination_shema import PaginationSchema
from api.v1.view_models import FilmShort, Person
from services.movie_service import MovieService
from services.service_locator import get_film_service, get_person_service

router = APIRouter()


# Внедряем PersonService с помощью Depends(get_film_service)
@router.get(
    '/{person_id}',
    response_model=Person,
    summary="Person by person ID",
    description="Gets full information about given person"
)
async def person_details(person_id: str, person_service: MovieService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person not found')

    return Person.parse_obj(person)


# Внедряем PersonService с помощью Depends(get_film_service)
@router.get(
    '/',
    summary="List all person",
    description=""
)
async def person_list(pagination: PaginationSchema = Depends(),
                      person_service: MovieService = Depends(get_person_service)) -> list[Person]:
    persons = await person_service.uber_get(pagination=pagination)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person not found')

    return [Person.parse_obj(person) for person in persons]


# Внедряем PersonService с помощью Depends(get_film_service)
@router.get(
    '/search/',
    summary="Full text search person ",
    description="Search over database, search fields is full_name."
)
async def person_list(query: Optional[str],
                      pagination: PaginationSchema = Depends(),
                      person_service: MovieService = Depends(get_person_service)) -> list[Person]:
    persons = await person_service.uber_get(pagination=pagination,
                                            search_value=query,
                                            search_fields=['full_name']
                                            )
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person not found')

    return [Person.parse_obj(person) for person in persons]


@router.get(
    '/{person_id}/film/',
    summary="Film by person ID",
    description="Gets films by given person"
)
async def film_list(person_id: Optional[str] = None,
                    film_service: MovieService = Depends(get_film_service)) -> list[FilmShort]:
    films = await film_service.uber_get(search_value=person_id,
                                        property_list=['actors.id', 'directors.id', 'writers.id']
                                        )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return [FilmShort.parse_obj(film) for film in films]
