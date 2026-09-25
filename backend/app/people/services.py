from app.movies.models import DimMovie
from sqlalchemy.ext.asyncio import AsyncSession
from app.people.crud import CRUDPeople
from app.people.models import DimPeople


class PeopleService:
    def __init__(self, db: AsyncSession):
        self.crud = CRUDPeople(db)
    
    def get_person_by_id(self, id_pessoa: str) -> DimPeople | None:
        return self.crud.get_person_by_id(id_pessoa)
    
    async def list_people(
        self,
        nome_pessoa: str | None = None,
        tipo_pessoa: str | None = None,
        page: int = 1,
        size: int = 20,
    ):
        """Lista pessoas com busca por nome, múltiplos filtros e paginação."""
        offset = (page - 1) * size

        people, total = await self.crud.list_people(
            nome_pessoa=nome_pessoa,
            tipo_pessoa=tipo_pessoa,
            offset=offset,
            limit=size,
        )

        pages = (total + size - 1) // size

        return {
            "items": people,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
        }

    async def list_people_by_movie(self, id_filme: str) -> list[DimPeople]:
        return await self.crud.list_people_by_movie(id_filme)

    async def get_movies_by_person(
        self,
        sk_person_id: str,
    ) -> list[DimMovie]:
        return await self.crud.get_movies_by_person(sk_person_id)