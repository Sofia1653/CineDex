"""Modelo ORM do domínio de avaliações (reviews) do RocketLab 2026.2.

Contém as avaliações individuais submetidas por usuários (movie_reviews)
e o resumo consolidado de métricas por filme (dim_reviews).
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Double,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, generate_surrogate_key

if TYPE_CHECKING:
    from app.movies.models import DimMovie


class MovieReview(Base):
    """Avaliação individual de um filme na escala de 0 a 10."""

    __tablename__ = "movie_reviews"
    __table_args__ = (CheckConstraint("nota >= 0 AND nota <= 10", name="nota_range"),)

    sk_movie_review_id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=generate_surrogate_key
    )
    sk_movie_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dim_movies.sk_movie_id", ondelete="CASCADE"), index=True
    )
    nome: Mapped[str] = mapped_column(String(120))
    nota: Mapped[float] = mapped_column(Double)
    comentario: Mapped[str] = mapped_column(String(4000))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    movie: Mapped["DimMovie"] = relationship("DimMovie", back_populates="reviews")


class DimReview(Base):
    """Resumo consolidado de avaliações por filme."""

    __tablename__ = "dim_reviews"

    sk_review_id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=generate_surrogate_key
    )
    sk_movie_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dim_movies.sk_movie_id", ondelete="CASCADE"), unique=True
    )
    qtd_avaliacoes_usuarios: Mapped[int] = mapped_column(Integer, default=0)
    nota_media_usuarios: Mapped[float | None] = mapped_column(Double, default=None)

    movie: Mapped["DimMovie"] = relationship("DimMovie", back_populates="reviews_summary")


# Garante registro de DimMovie no Base.metadata para resolução de relacionamentos
import app.movies.models as _movies_models  # noqa: E402, F401

__all__ = ["DimReview", "MovieReview"]
