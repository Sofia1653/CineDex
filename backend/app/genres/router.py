from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.genres.schemas import (
    GenreListResponse,
    GenreMovieListResponse,
    GenreResponse,
)
from app.genres.services import GenreService

router = APIRouter(
    prefix="/genres",
    tags=["genres"],
)


def get_genre_service(
    db: AsyncSession = Depends(get_db),
) -> GenreService:
    return GenreService(db)


@router.get(
    "",
    response_model=GenreListResponse,
)
async def list_genres(
    service: GenreService = Depends(get_genre_service),
):
    return await service.list_genres()


@router.get(
    "/{sk_genre_id}",
    response_model=GenreResponse,
)
async def get_genre(
    sk_genre_id: str,
    service: GenreService = Depends(get_genre_service),
):
    genre = await service.get_genre_by_id(sk_genre_id)

    if genre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gênero não encontrado",
        )

    return genre


@router.get(
    "/{sk_genre_id}/movies",
    response_model=GenreMovieListResponse,
)
async def get_genre_movies(
    sk_genre_id: str,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: GenreService = Depends(get_genre_service),
):
    genre = await service.get_genre_by_id(sk_genre_id)

    if genre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gênero não encontrado",
        )

    return await service.get_movies_by_genre(sk_genre_id, page=page, size=size)
