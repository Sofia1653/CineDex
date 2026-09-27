from pydantic import BaseModel, ConfigDict, HttpUrl


class GenreResponse(BaseModel):
    sk_genre_id: str
    nome_genero: str

    model_config = ConfigDict(from_attributes=True)


class GenreListItem(GenreResponse):
    qtd_filmes: int = 0


class GenreListResponse(BaseModel):
    items: list[GenreListItem]
    total: int


class GenreMovieItem(BaseModel):
    sk_movie_id: str
    id_filme: str
    titulo: str
    ano_lancamento: int | None = None
    url_poster: HttpUrl | None = None

    model_config = ConfigDict(from_attributes=True)


class GenreMovieListResponse(BaseModel):
    items: list[GenreMovieItem]
    total: int
