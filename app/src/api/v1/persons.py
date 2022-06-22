from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from api.v1.utility import validate_order_field
from services.service_locator import get_film_service, get_genre_service, get_person_service
from services.movie_service import MovieService

from models.models import init_from

from api.v1.view_models import Film, FilmShort, Person

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

    send_person = convert_person(person)
    return send_person


# Внедряем PersonService с помощью Depends(get_film_service)
@router.get(
    '/',
    summary="List all person",
    description=""
)
async def person_list(page_size: Optional[int] = 50,
                      page_number: Optional[int] = 1,
                      person_service: MovieService = Depends(get_person_service)) -> list[Person]:
    persons = await person_service.uber_get(page_size=page_size,
                                            page_number=page_number
                                            )
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person not found')

    result = [convert_person(person) for person in persons]
    return result


# Внедряем PersonService с помощью Depends(get_film_service)
@router.get(
    '/search/',
    summary="Full text search person ",
    description="Search over database, search fields is full_name."
)
async def person_list(query: Optional[str],
                      page_size: Optional[int] = 50,
                      page_number: Optional[int] = 1,
                      person_service: MovieService = Depends(get_person_service)) -> list[Person]:
    persons = await person_service.uber_get(page_size=page_size,
                                            page_number=page_number,
                                            search_value=query,
                                            search_fields=['full_name']
                                            )
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Person not found')

    result = [init_from(Person, person) for person in persons]
    return result


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

    result = [init_from(FilmShort, film) for film in films]
    return result
