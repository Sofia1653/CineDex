from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ReviewSummaryResponse(BaseModel):
    sk_review_id: str
    sk_movie_id: str
    qtd_avaliacoes_usuarios: int = 0
    nota_media_usuarios: float | None = None

    model_config = ConfigDict(from_attributes=True)

class MovieReviewCreate(BaseModel):
    nome: str = Field(default="Anônimo", max_length=120)
    nota: float = Field(..., ge=0.0, le=10.0, description="Nota de 0 a 5")
    comentario: str = Field(..., max_length=4000)

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
