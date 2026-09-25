from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

NOTA_MIN = 0.0
NOTA_MAX = 10.0


class MovieReviewCreate(BaseModel):
    nome: str = Field(default="Anônimo", max_length=120)
    nota: float = Field(
        ...,
        ge=NOTA_MIN,
        le=NOTA_MAX,
        description="Nota de 0 a 10",
    )
    comentario: str = Field(default="", max_length=4000)


class MovieReviewUpdate(BaseModel):
    nome: str | None = Field(default=None, max_length=120)
    nota: float | None = Field(default=None, ge=NOTA_MIN, le=NOTA_MAX)
    comentario: str | None = Field(default=None, max_length=4000)


class MovieReviewResponse(BaseModel):
    sk_movie_review_id: str
    sk_movie_id: str
    nome: str
    nota: float
    comentario: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MovieReviewListResponse(BaseModel):
    items: list[MovieReviewResponse]
    total: int
    page: int
    size: int
    pages: int


class ReviewSummaryResponse(BaseModel):
    sk_review_id: str | None = None
    sk_movie_id: str
    qtd_avaliacoes_usuarios: int = 0
    nota_media_usuarios: float | None = None

    model_config = ConfigDict(from_attributes=True)
