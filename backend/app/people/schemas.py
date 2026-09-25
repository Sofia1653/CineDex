from typing import Literal
from pydantic import BaseModel, ConfigDict

PersonType = Literal["Ator", "Diretor", "Roteirista"]

class PeopleResponse(BaseModel):
    sk_person_id: str
    nome_pessoa: str
    tipo_pessoa: PersonType

    model_config = ConfigDict(from_attributes=True)

class PersonMovieItem(BaseModel):
    sk_movie_id: str
    id_filme: str
    titulo: str
    ano_lancamento: int | None = None

    model_config = ConfigDict(from_attributes=True)

class PersonDetailsResponse(PeopleResponse):
    movies: list[PersonMovieItem] = []
