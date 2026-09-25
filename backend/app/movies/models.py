"""Modelo ORM do catálogo de filmes do RocketLab 2026.2.

O domínio foi organizado como esquema estrela para suportar consultas
analíticas, mantendo relações de navegação úteis para a futura API.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Column,
    Date,
    Double,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, generate_surrogate_key

bridge_movie_genre = Table(
    "bridge_movie_genre",
    Base.metadata,
    Column(
        "sk_movie_id",
        String(64),
        ForeignKey("dim_movies.sk_movie_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "sk_genre_id",
        String(64),
        ForeignKey("dim_genres.sk_genre_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

bridge_movie_company = Table(
    "bridge_movie_company",
    Base.metadata,
    Column(
        "sk_movie_id",
        String(64),
        ForeignKey("dim_movies.sk_movie_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "sk_company_id",
        String(64),
        ForeignKey("dim_companies.sk_company_id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

bridge_movie_person = Table(
    "bridge_movie_person",
    Base.metadata,
    Column(
        "sk_movie_id",
        String(64),
        ForeignKey("dim_movies.sk_movie_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "sk_person_id",
        String(64),
        ForeignKey("dim_people.sk_person_id", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    ),
)


class DimMovie(Base):
    """Metadados descritivos de um filme."""

    __tablename__ = "dim_movies"

    sk_movie_id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=generate_surrogate_key
    )
    id_filme: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    titulo: Mapped[str] = mapped_column(String(500), index=True)
    data_lancamento: Mapped[date | None] = mapped_column(Date, default=None)
    ano_lancamento: Mapped[int | None] = mapped_column(Integer, index=True, default=None)
    duracao_minutos: Mapped[int | None] = mapped_column(Integer, default=None)
    status_filme: Mapped[str | None] = mapped_column(String(50), default=None)
    sinopse: Mapped[str | None] = mapped_column(String(4000), default=None)
    url_poster: Mapped[str | None] = mapped_column(String(2048), default=None)
    url_backdrop: Mapped[str | None] = mapped_column(String(2048), default=None)

    genres: Mapped[list["DimGenre"]] = relationship(
        secondary=bridge_movie_genre, back_populates="movies", order_by="DimGenre.nome_genero"
    )
    companies: Mapped[list["DimCompany"]] = relationship(
        secondary=bridge_movie_company,
        back_populates="movies",
        order_by="DimCompany.nome_produtora",
    )
    people: Mapped[list["DimPerson"]] = relationship(
        secondary=bridge_movie_person, back_populates="movies"
    )
    performance: Mapped["FactMoviePerformance | None"] = relationship(
        back_populates="movie", cascade="all, delete-orphan", uselist=False
    )
    reviews_summary: Mapped["DimReview | None"] = relationship(
        back_populates="movie", cascade="all, delete-orphan", uselist=False
    )
    reviews: Mapped[list["MovieReview"]] = relationship(
        back_populates="movie", cascade="all, delete-orphan", order_by="MovieReview.created_at"
    )


class DimGenre(Base):
    """Catálogo deduplicado de gêneros."""

    __tablename__ = "dim_genres"

    sk_genre_id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=generate_surrogate_key
    )
    nome_genero: Mapped[str] = mapped_column(String(50), unique=True)

    movies: Mapped[list[DimMovie]] = relationship(
        secondary=bridge_movie_genre, back_populates="genres"
    )


class DimCompany(Base):
    """Catálogo deduplicado de produtoras e estúdios."""

    __tablename__ = "dim_companies"

    sk_company_id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=generate_surrogate_key
    )
    nome_produtora: Mapped[str] = mapped_column(String(255), unique=True)

    movies: Mapped[list[DimMovie]] = relationship(
        secondary=bridge_movie_company, back_populates="companies"
    )


class FactMoviePerformance(Base):
    """Métricas financeiras e de engajamento; uma ocorrência por filme."""

    __tablename__ = "fact_movies_performance"

    sk_movie_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("dim_movies.sk_movie_id", ondelete="CASCADE"), primary_key=True
    )
    orcamento_usd: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), default=None)
    receita_usd: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), default=None)
    lucro_usd: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    orcamento_brl: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), default=None)
    receita_brl: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), default=None)
    lucro_brl: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    popularidade: Mapped[float | None] = mapped_column(Double, default=None)
    nota_tmdb: Mapped[float | None] = mapped_column(Double, default=None)
    qtd_tmdb: Mapped[int | None] = mapped_column(Integer, default=None)
    nota_imdb: Mapped[float | None] = mapped_column(Double, default=None)
    qtd_imdb: Mapped[int | None] = mapped_column(Integer, default=None)

    movie: Mapped[DimMovie] = relationship(back_populates="performance")


# Reexporta os modelos e tipos dos domínios people e reviews para retrocompatibilidade
from app.people.models import PERSON_TYPES, DimPerson, PersonType  # noqa: E402
from app.reviews.models import DimReview, MovieReview  # noqa: E402

__all__ = [
    "Base",
    "DimCompany",
    "DimGenre",
    "DimMovie",
    "DimPerson",
    "DimReview",
    "FactMoviePerformance",
    "MovieReview",
    "PERSON_TYPES",
    "PersonType",
    "bridge_movie_company",
    "bridge_movie_genre",
    "bridge_movie_person",
    "generate_surrogate_key",
]

