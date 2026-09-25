from datetime import date
from pydantic import BaseModel, ConfigDict, HttpUrl


class MovieBase(BaseModel):
    titulo: str
    data_lancamento: date | None = None
    ano_lancamento: int | None = None
    duracao_minutos: int | None = None
    status_filme: str | None = None
    sinopse: str | None = None
    url_poster: HttpUrl | None = None
    url_backdrop: HttpUrl | None = None

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

class MovieResponse(MovieBase):
    sk_movie_id: str
    id_filme: str

    model_config = ConfigDict(from_attributes=True)

class MovieListResponse(BaseModel):
    items: list[MovieResponse]
    total: int
    page: int
    size: int
    pages: int