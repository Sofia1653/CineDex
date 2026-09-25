from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.movies.models import DimMovie, bridge_movie_person
from app.people.models import DimPerson


class CRUDPeople:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_person_by_id(self, sk_person_id: str) -> DimPerson | None:
        """Busca a pessoa pela surrogate key (chave primária interna)."""
        return await self.db.get(DimPerson, sk_person_id)

    async def list_people(
        self,
        *,
        nome_pessoa: str | None = None,
        tipo_pessoa: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[DimPerson], int]:
        """Lista pessoas com busca por nome, múltiplos filtros e paginação."""
        query = select(DimPerson)

        if nome_pessoa and nome_pessoa.strip():
            query = query.where(DimPerson.nome_pessoa.ilike(f"%{nome_pessoa.strip()}%"))

        if tipo_pessoa and tipo_pessoa.strip():
            query = query.where(DimPerson.tipo_pessoa.ilike(f"%{tipo_pessoa.strip()}%"))

        count_stmt = select(func.count()).select_from(query.order_by(None).subquery())
        total = (await self.db.scalar(count_stmt)) or 0

        paged_query = query.order_by(DimPerson.nome_pessoa.asc()).offset(offset).limit(limit)

        result = await self.db.execute(paged_query)

        return list(result.scalars().all()), total

    async def list_people_by_movie(self, id_filme: str) -> list[DimPerson]:
        """Lista as pessoas vinculadas a um filme, sem duplicatas por papel."""
        query = (
            select(DimPerson)
            .join(bridge_movie_person, bridge_movie_person.c.sk_person_id == DimPerson.sk_person_id)
            .join(DimMovie, DimMovie.sk_movie_id == bridge_movie_person.c.sk_movie_id)
            .where(DimMovie.id_filme == id_filme)
            .order_by(DimPerson.nome_pessoa.asc())
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_movies_by_person(
        self,
        sk_person_id: str,
    ) -> list[DimMovie]:
        query = (
            select(DimMovie)
            .join(bridge_movie_person, bridge_movie_person.c.sk_movie_id == DimMovie.sk_movie_id)
            .where(bridge_movie_person.c.sk_person_id == sk_person_id)
            .order_by(DimMovie.ano_lancamento.desc().nullslast(), DimMovie.titulo.asc())
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())
