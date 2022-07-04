import typing as t

from models.models import ORJSONModel


class GenreShort(ORJSONModel):
    id: str
    name: str


class PersonShort(ORJSONModel):
    id: str
    name: str


class Film(ORJSONModel):
    id: str
    imdb_rating: t.Optional[float]
    title: t.Optional[str]
    description: t.Optional[str]
    genres: t.Optional[t.List[GenreShort]]
    directors: t.Optional[t.List[PersonShort]]
    actors: t.Optional[t.List[PersonShort]]
    writers: t.Optional[t.List[PersonShort]]


class FilmShort(ORJSONModel):
    id: str
    title: t.Optional[str]
    imdb_rating: t.Optional[float]


class FilmMid(ORJSONModel):
    id: str
    title: t.Optional[str]
    imdb_rating: t.Optional[float]
    description: t.Optional[str]


class FilmIds(ORJSONModel):
    id: str


class FilmRoles(ORJSONModel):
    id: str
    name: str


class Person(ORJSONModel):
    id: str
    full_name: str
    film_roles: t.List[FilmRoles]


class Genre(ORJSONModel):
    id: str
    name: str
    description: t.Optional[str]
