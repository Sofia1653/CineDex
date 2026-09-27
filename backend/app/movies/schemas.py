from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.genres.schemas import GenreResponse
from app.people.schemas import PeopleResponse
from app.reviews.schemas import ReviewSummaryResponse

PersonRole = Literal["Ator", "Diretor", "Roteirista"]


class MoviePersonInput(BaseModel):
    """Pessoa informada no cadastro do filme, identificada por nome e papel."""

    nome_pessoa: str = Field(..., min_length=1, max_length=255)
    tipo_pessoa: PersonRole


class MovieBase(BaseModel):
    titulo: str
    data_lancamento: date | None = None
    ano_lancamento: int | None = None
    duracao_minutos: int | None = None
    status_filme: str | None = None
    sinopse: str | None = None
    url_poster: HttpUrl | None = None
    url_backdrop: HttpUrl | None = None
    genres: list[str] = Field(default_factory=list)
    pessoas: list[MoviePersonInput] = Field(default_factory=list)

class MovieCreate(MovieBase):
    id_filme: str | None = None

class MovieUpdate(BaseModel):
    titulo: str | None = None
    data_lancamento: date | None = None
    ano_lancamento: int | None = None
    duracao_minutos: int | None = None
    status_filme: str | None = None
    sinopse: str | None = None
    url_poster: HttpUrl | None = None
    url_backdrop: HttpUrl | None = None
    genres: list[str] | None = None
    pessoas: list[MoviePersonInput] | None = None

class MovieResponse(MovieBase):
    sk_movie_id: str
    id_filme: str
    genres: list[GenreResponse] = Field(default_factory=list)
    pessoas: list[PeopleResponse] = Field(default_factory=list, validation_alias="people")
    review_summary: ReviewSummaryResponse | None = Field(
        default=None,
        validation_alias="reviews_summary",
    )
    model_config = ConfigDict(from_attributes=True)

class MovieListResponse(BaseModel):
    items: list[MovieResponse]
    total: int
    page: int
    size: int
    pages: int
