from sqlalchemy.ext.asyncio import AsyncSession

from app.genres.crud import CRUDGenre
from app.movies.models import DimGenre


class GenreService:
    def __init__(self, db: AsyncSession):
        self.crud = CRUDGenre(db)

    async def get_genre_by_id(self, sk_genre_id: str) -> DimGenre | None:
        return await self.crud.get_genre_by_id(sk_genre_id)

    async def list_genres(self) -> dict[str, object]:
        """Catálogo completo de gêneros, já com a contagem de filmes."""
        rows = await self.crud.list_genres()

        return {
            "items": [
                {
                    "sk_genre_id": genre.sk_genre_id,
                    "nome_genero": genre.nome_genero,
                    "qtd_filmes": qtd,
                }
                for genre, qtd in rows
            ],
            "total": len(rows),
        }

    async def get_movies_by_genre(
        self,
        sk_genre_id: str,
        page: int = 1,
        size: int = 20,
    ) -> dict[str, object]:
        offset = (page - 1) * size

        movies, total = await self.crud.get_movies_by_genre(
            sk_genre_id,
            limit=size,
            offset=offset,
        )

        return {
            "items": movies,
            "total": total,
        }
