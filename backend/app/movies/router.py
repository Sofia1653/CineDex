from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.movies.schemas import (
    MovieCreate,
    MovieListResponse,
    MovieResponse,
    MovieUpdate,
)
from .services import MovieService


router = APIRouter(
    prefix="/movies",
    tags=["movies"],
)


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
    "",
    response_model=MovieListResponse,
)
async def list_movies(
    titulo: str | None = Query(default=None),
    ano: int | None = Query(default=None, ge=1800),
    genero: str | None = Query(default=None),
    status_filme: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
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
    id_filme: str,
    service: MovieService = Depends(get_movie_service),
):
    movie = await service.get_movie_by_id_filme(id_filme)

    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filme não encontrado",
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
            detail="Filme não encontrado",
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
            detail="Filme não encontrado",
        )

    return None