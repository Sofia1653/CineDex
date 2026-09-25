from app.movies.models import DimMovie
from sqlalchemy.ext.asyncio import AsyncSession
from app.people.models import DimPeople
from sqlalchemy import select, func

class CRUDPeople:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_person_by_id(self, id_pessoa: str) -> DimPeople | None:
        """Busca a pessoa pelo id_pessoa"""
        query = select(DimPeople).where(DimPeople.id_pessoa == id_pessoa)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def list_people(
        self,
        *,
        nome_pessoa: str | None = None,
        tipo_pessoa: str | None = None,
        offset: int = 1,
        limit: int = 20,
    ) -> tuple[list[DimPeople], int]:
        """Lista pessoas com busca por nome, múltiplos filtros e paginação."""
        query = select(DimPeople)

        if nome_pessoa and nome_pessoa.strip():
            query = query.where(DimPeople.nome_pessoa.ilike(f"%{nome_pessoa.strip()}%"))

        if tipo_pessoa and tipo_pessoa.strip():
            query = query.where(DimPeople.tipo_pessoa.ilike(f"%{tipo_pessoa.strip()}%"))

        count_stmt = select(func.count()).select_from(query.order_by(None).subquery())
        total = (await self.db.scalar(count_stmt)) or 0

        paged_query = (
            query.order_by(DimPeople.nome_pessoa.asc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(paged_query)
        people = list(result.scalars().all())

        return people, total
    
    async def list_people_by_movie(self, id_filme: str) -> list[DimPeople]:
        """Lista pessoas por filme."""
        query = select(DimPeople).where(DimPeople.id_filme == id_filme)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_movies_by_person(
        self,
        sk_person_id: str,
    ) -> list[DimMovie]:
        query = (
            select(DimMovie)
            .join(DimMovie.people)
            .where(DimPeople.sk_person_id == sk_person_id)
            .order_by(DimMovie.ano_lancamento.desc().nullslast())
        )

        result = await self.db.execute(query)
        return list(result.scalars().all())