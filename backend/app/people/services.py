from sqlalchemy.ext.asyncio import AsyncSession

from app.people.crud import CRUDPeople
from app.people.models import DimPerson


class PeopleService:
    def __init__(self, db: AsyncSession):
        self.crud = CRUDPeople(db)

    async def get_person_by_id(self, sk_person_id: str) -> DimPerson | None:
        return await self.crud.get_person_by_id(sk_person_id)

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

    async def list_people_by_movie(self, id_filme: str) -> list[DimPerson]:
        return await self.crud.list_people_by_movie(id_filme)

    async def get_movies_by_person(
        self,
        sk_person_id: str,
    ) -> dict[str, object]:
        movies = await self.crud.get_movies_by_person(sk_person_id)

        return {
            "items": movies,
            "total": len(movies),
        }
