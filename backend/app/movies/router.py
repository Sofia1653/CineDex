from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.movies.schemas import (
    MovieCreate,
    MovieListResponse,
    MovieResponse,
    MovieStatusListResponse,
    MovieUpdate,
)

from .services import MovieService

router = APIRouter(
    prefix="/movies",
    tags=["movies"],
)

ANO_MIN = 1800
ANO_MAX = 2100


def get_movie_service(
    db: AsyncSession = Depends(get_db),
) -> MovieService:
    return MovieService(db)


@router.post(
    "",
    response_model=MovieResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_movie(
    movie: MovieCreate,
    service: MovieService = Depends(get_movie_service),
):
    return await service.create_movie(movie)


@router.get(
    "/status",
    response_model=MovieStatusListResponse,
    summary="Lista os status de filme existentes no catálogo",
)
async def list_movie_statuses(service: MovieService = Depends(get_movie_service)):
    return await service.list_statuses()


@router.get(
    "",
    response_model=MovieListResponse,
)
async def list_movies(
    titulo: str | None = Query(default=None, description="Busca parcial pelo título"),
    ano: int | None = Query(
        default=None,
        ge=ANO_MIN,
        le=ANO_MAX,
        description=f"Ano exato de lançamento, entre {ANO_MIN} e {ANO_MAX}",
    ),
    genero: str | None = Query(default=None, description="Gênero do filme"),
    status_filme: str | None = Query(default=None, description="Status do filme"),
    page: int = Query(default=1, ge=1, description="Página desejada, começando em 1"),
    size: int = Query(default=24, ge=1, le=100, description="Filmes por página"),
    service: MovieService = Depends(get_movie_service),
):
    return await service.list_movies(
        titulo=titulo,
        ano=ano,
        genero=genero,
        status_filme=status_filme,
        page=page,
        size=size,
    )


@router.get(
    "/{id_filme}",
    response_model=MovieResponse,
)
async def get_movie(
    id_filme: str = Path(description="Identificador público do filme"),
    service: MovieService = Depends(get_movie_service),
):
    movie = await service.get_movie_by_id_filme(id_filme, load_relations=True)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não encontramos o filme '{id_filme}'.",
        )

    return movie


@router.put(
    "/{id_filme}",
    response_model=MovieResponse,
)
async def update_movie(
    id_filme: str,
    movie: MovieUpdate,
    service: MovieService = Depends(get_movie_service),
):
    updated_movie = await service.update_movie(
        id_filme,
        movie,
    )

    if updated_movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não encontramos o filme '{id_filme}' para atualizar.",
        )

    return updated_movie


@router.delete(
    "/{id_filme}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_movie(
    id_filme: str,
    service: MovieService = Depends(get_movie_service),
):
    movie = await service.delete_movie(id_filme)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Não encontramos o filme '{id_filme}' para remover.",
        )

    return None