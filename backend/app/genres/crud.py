from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.movies.models import DimGenre, DimMovie, bridge_movie_genre


class CRUDGenre:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_genre_by_id(self, sk_genre_id: str) -> DimGenre | None:
        """Busca o gênero pela surrogate key (chave primária interna)."""
        return await self.db.get(DimGenre, sk_genre_id)

    async def get_genre_by_name(self, nome_genero: str) -> DimGenre | None:
        """Busca o gênero pelo nome exato."""
        result = await self.db.execute(
            select(DimGenre).where(DimGenre.nome_genero == nome_genero)
        )
        return result.scalar_one_or_none()

    async def list_genres(self) -> list[tuple[DimGenre, int]]:
        """Lista o catálogo de gêneros com a quantidade de filmes de cada um."""
        count_filmes = (
            select(func.count(bridge_movie_genre.c.sk_movie_id))
            .where(bridge_movie_genre.c.sk_genre_id == DimGenre.sk_genre_id)
            .correlate(DimGenre)
            .scalar_subquery()
        )

        result = await self.db.execute(
            select(DimGenre, count_filmes.label("qtd_filmes")).order_by(
                DimGenre.nome_genero.asc()
            )
        )

        return list(result.all())

    async def get_movies_by_genre(
        self,
        sk_genre_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[DimMovie], int]:
        """Lista paginada dos filmes vinculados a um gênero."""
        base = select(DimMovie).join(
            bridge_movie_genre,
            bridge_movie_genre.c.sk_movie_id == DimMovie.sk_movie_id,
        )

        filters = (bridge_movie_genre.c.sk_genre_id == sk_genre_id,)

        total = (
            await self.db.scalar(
                select(func.count()).select_from(base.where(*filters).subquery())
            )
        ) or 0

        result = await self.db.execute(
            base.where(*filters)
            .order_by(DimMovie.ano_lancamento.desc().nullslast(), DimMovie.titulo.asc())
            .offset(offset)
            .limit(limit)
        )

        return list(result.scalars().all()), total
