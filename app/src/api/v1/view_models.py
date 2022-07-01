from typing import Optional

from models.models import ORJSONModel


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


class FilmShort(ORJSONModel):
    id: str
    title: Optional[str]
    imdb_rating: Optional[float]


class FilmMid(ORJSONModel):
    id: str
    title: Optional[str]
    imdb_rating: Optional[float]
    description: Optional[str]


class FilmIds(ORJSONModel):
    id: str


class FilmRoles(ORJSONModel):
    id: str
    name: str


class Person(ORJSONModel):
    id: str
    full_name: str
    film_roles: list[FilmRoles]


class Genre(ORJSONModel):
    id: str
    name: str
    description: Optional[str]
