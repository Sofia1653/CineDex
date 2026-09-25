from pydantic import BaseModel

class ReviewCreate(BaseModel):
    sk_review_id: str
    sk_movie_id: str
    qtd_avaliacoes_usuarios: int
    nota_media_usuarios: float
