from app.movies.schemas import MovieUpdate
from app.movies.schemas import MovieCreate
from app.movies.models import DimMovie
from sqlalchemy.ext.asyncio import AsyncSession
from app.movies.crud import CRUDMovie
    

class MovieService:
    def __init__(self, db: AsyncSession):
        self.crud = CRUDMovie(db)

    # Paginação 
    async def list_movies(
        self,
        titulo: str | None = None,
        ano: int | None = None,
        genero: str | None = None,
        status_filme: str | None = None,
        page: int = 1,
        size: int = 20,
    ):
        offset = (page - 1) * size

        movies, total = await self.crud.list_movies(
            titulo=titulo,
            ano=ano,
            genero=genero,
            status_filme=status_filme,
            offset=offset,
            limit=size,
        )

        pages = (total + size - 1) // size

        return {
            "items": movies,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages,
        }
    
    async def create_movie(self, movie: MovieCreate) -> DimMovie:
        return await self.crud.create_movie(movie)
    
    async def get_movie_by_id_filme(self, id_filme: str, load_relations: bool = False) -> DimMovie | None:
        return await self.crud.get_movie_by_id_filme(id_filme, load_relations)
    
    async def get_movie_by_sk(self, sk_movie_id: str) -> DimMovie | None:
        return await self.crud.get_movie_by_sk(sk_movie_id)
    
    async def update_movie(self, id_filme: str, movie: MovieUpdate) -> DimMovie | None:
        return await self.crud.update_movie(id_filme, movie)
    
    async def delete_movie(self, id_filme: str) -> DimMovie | None:
        return await self.crud.delete_movie(id_filme)