from uuid import uuid4
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.movies.models import DimGenre, DimMovie
from app.movies.schemas import MovieCreate, MovieUpdate

class CRUDMovie:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_movie(self, movie: MovieCreate) -> DimMovie:
        movie_data = movie.model_dump()
        
        if not movie_data.get("id_filme"):
            movie_data["id_filme"] = f"mov_{uuid4().hex[:12]}"

        if movie_data.get("url_poster"):
            movie_data["url_poster"] = str(movie_data["url_poster"])
        if movie_data.get("url_backdrop"):
            movie_data["url_backdrop"] = str(movie_data["url_backdrop"])

        db_movie = DimMovie(**movie_data)
        self.db.add(db_movie)
        await self.db.commit()
        await self.db.refresh(db_movie)
        return db_movie

    async def get_movie_by_id_filme(
        self, id_filme: str, load_relations: bool = False
    ) -> DimMovie | None:
        """Busca o filme pelo identificador de negócio id_filme."""
        query = select(DimMovie).where(DimMovie.id_filme == id_filme)
        if load_relations:
            query = query.options(
                selectinload(DimMovie.genres),
                selectinload(DimMovie.people),
                selectinload(DimMovie.performance),
                selectinload(DimMovie.reviews_summary),
            )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_movie_by_sk(self, sk_movie_id: str) -> DimMovie | None:
        """Busca pela surrogate key (chave primária interna)."""
        return await self.db.get(DimMovie, sk_movie_id)

    async def list_movies(
        self,
        *,
        titulo: str | None = None,
        ano: int | None = None,
        genero: str | None = None,
        status_filme: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[DimMovie], int]:
        """Lista filmes com busca por nome, múltiplos filtros e paginação."""
        query = select(DimMovie)

        # 1. Filtro de busca por nome (case-insensitive com ILIKE / LIKE)
        if titulo and titulo.strip():
            query = query.where(DimMovie.titulo.ilike(f"%{titulo.strip()}%"))

        # 2. Filtro por ano de lançamento
        if ano is not None:
            query = query.where(DimMovie.ano_lancamento == ano)

        # 3. Filtro por status do filme
        if status_filme and status_filme.strip():
            query = query.where(DimMovie.status_filme.ilike(f"%{status_filme.strip()}%"))

        # 4. Filtro por gênero (faz join com DimGenre)
        if genero and genero.strip():
            query = query.join(DimMovie.genres).where(
                DimGenre.nome_genero.ilike(f"%{genero.strip()}%")
            )

        # Calcula o total de registros considerando os mesmos filtros aplicados
        count_stmt = select(func.count()).select_from(query.order_by(None).subquery())
        total = (await self.db.scalar(count_stmt)) or 0

        # Aplica ordenação padrão e paginação
        paged_query = (
            query.order_by(DimMovie.ano_lancamento.desc().nullslast(), DimMovie.titulo.asc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(paged_query)
        movies = list(result.scalars().all())

        return movies, total

    async def update_movie(self, id_filme: str, movie: MovieUpdate) -> DimMovie | None:
        db_movie = await self.get_movie_by_id_filme(id_filme)
        if db_movie is None:
            return None

        update_data = movie.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in ("url_poster", "url_backdrop") and value is not None:
                value = str(value)
            setattr(db_movie, field, value)

        await self.db.commit()
        await self.db.refresh(db_movie)
        return db_movie

    async def delete_movie(self, id_filme: str) -> DimMovie | None:
        db_movie = await self.get_movie_by_id_filme(id_filme)
        if db_movie is None:
            return None

        await self.db.delete(db_movie)
        await self.db.commit()
        return db_movie
