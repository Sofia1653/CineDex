from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PersonType = Literal["Ator", "Diretor", "Roteirista"]


class PeopleResponse(BaseModel):
    sk_person_id: str
    nome_pessoa: str
    tipo_pessoa: PersonType

    model_config = ConfigDict(from_attributes=True)


class PeopleListResponse(BaseModel):
    items: list[PeopleResponse]
    total: int
    page: int
    size: int
    pages: int


class PersonMovieItem(BaseModel):
    sk_movie_id: str
    id_filme: str
    titulo: str
    ano_lancamento: int | None = None

    model_config = ConfigDict(from_attributes=True)


class PersonMovieListResponse(BaseModel):
    items: list[PersonMovieItem]
    total: int


class PersonDetailsResponse(PeopleResponse):
    movies: list[PersonMovieItem] = Field(default_factory=list)
