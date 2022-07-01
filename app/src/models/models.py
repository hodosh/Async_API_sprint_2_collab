from typing import Any
from typing import Optional

import orjson
from pydantic import BaseModel


def orjson_dumps(v: Any, *, default: Any) -> str:
    return orjson.dumps(v, default=default).decode()


def init_from(new_class, ref_obj):
    prop = [i for i in ref_obj.__dict__.keys() if i[:1] != '_']
    new_args = {}
    for k in prop:
        new_args[k] = getattr(ref_obj, k)
    return new_class(**new_args)


class ORJSONModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class FilmIds(ORJSONModel):
    id: str


class FilmRoles(ORJSONModel):
    id: str
    name: str


class Genre(ORJSONModel):
    id: str
    name: str
    description: Optional[str]
    film_ids: list[FilmIds]


class Person(ORJSONModel):
    id: str
    full_name: str
    film_roles: list[FilmRoles]


class GenreShort(ORJSONModel):
    id: str
    name: str


class PersonShort(ORJSONModel):
    id: str
    name: str


class Film(ORJSONModel):
    id: str
    imdb_rating: Optional[float]
    title: Optional[str]
    description: Optional[str]
    genres: Optional[list[GenreShort]]
    directors: Optional[list[PersonShort]]
    actors: Optional[list[PersonShort]]
    writers: Optional[list[PersonShort]]
