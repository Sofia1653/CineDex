"""Modelo ORM do domínio de pessoas do RocketLab 2026.2.

Representa os profissionais do cinema (atores, diretores, roteiristas) e suas
associações com obras audiovisuais catalogadas.
"""

from typing import TYPE_CHECKING, Literal

from sqlalchemy import CheckConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, generate_surrogate_key

if TYPE_CHECKING:
    from app.movies.models import DimMovie

PERSON_TYPES: tuple[str, ...] = ("Ator", "Diretor", "Roteirista")
PersonType = Literal["Ator", "Diretor", "Roteirista"]


class DimPerson(Base):
    """Pessoa associada a um filme em um papel específico."""

    __tablename__ = "dim_people"
    __table_args__ = (
        UniqueConstraint(
            "nome_pessoa", "tipo_pessoa", name="uq_dim_people_nome_pessoa_tipo_pessoa"
        ),
        CheckConstraint(
            "tipo_pessoa IN (" + ", ".join(f"'{value}'" for value in PERSON_TYPES) + ")",
            name="tipo_pessoa_valido",
        ),
    )

    sk_person_id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=generate_surrogate_key
    )
    nome_pessoa: Mapped[str] = mapped_column(String(255), index=True)
    tipo_pessoa: Mapped[PersonType] = mapped_column(String(20))

    movies: Mapped[list["DimMovie"]] = relationship(
        "DimMovie", secondary="bridge_movie_person", back_populates="people"
    )


# Registra bridge_movie_person e DimMovie no Base.metadata para resolução de relacionamentos
import app.movies.models as _movies_models  # noqa: E402, F401

bridge_movie_person = _movies_models.bridge_movie_person

__all__ = ["DimPerson", "PERSON_TYPES", "PersonType", "bridge_movie_person"]
