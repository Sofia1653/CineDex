from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.reviews.schemas import (
    MovieReviewCreate,
    MovieReviewListResponse,
    MovieReviewResponse,
    MovieReviewUpdate,
    ReviewSummaryResponse,
)
from app.reviews.services import ReviewService

router = APIRouter(
    prefix="/reviews",
    tags=["reviews"],
)


def get_review_service(
    db: AsyncSession = Depends(get_db),
) -> ReviewService:
    return ReviewService(db)


@router.post(
    "/{sk_movie_id}",
    response_model=MovieReviewResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_review(
    sk_movie_id: str,
    review: MovieReviewCreate,
    service: ReviewService = Depends(get_review_service),
):
    return await service.create_review(sk_movie_id, review)


@router.get(
    "/{sk_movie_id}/reviews",
    response_model=MovieReviewListResponse,
)
async def list_reviews(
    sk_movie_id: str,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=100),
    service: ReviewService = Depends(get_review_service),
):
    return await service.list_reviews_by_movie(
        sk_movie_id,
        page=page,
        size=size,
    )


@router.get(
    "/{sk_movie_id}/summary",
    response_model=ReviewSummaryResponse,
)
async def get_review_summary(
    sk_movie_id: str,
    service: ReviewService = Depends(get_review_service),
):
    summary = await service.get_review_summary(sk_movie_id)

    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Filme não encontrado ou sem avaliações",
        )

    return summary


@router.get(
    "/{sk_movie_review_id}",
    response_model=MovieReviewResponse,
)
async def get_review(
    sk_movie_review_id: str,
    service: ReviewService = Depends(get_review_service),
):
    review = await service.get_review_by_id(sk_movie_review_id)

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review não encontrada",
        )

    return review


@router.put(
    "/{sk_movie_review_id}",
    response_model=MovieReviewResponse,
)
async def update_review(
    sk_movie_review_id: str,
    review: MovieReviewUpdate,
    service: ReviewService = Depends(get_review_service),
):
    updated_review = await service.update_review(sk_movie_review_id, review)

    if updated_review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review não encontrada",
        )

    return updated_review


@router.delete(
    "/{sk_movie_review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    sk_movie_review_id: str,
    service: ReviewService = Depends(get_review_service),
):
    review = await service.delete_review(sk_movie_review_id)

    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review não encontrada",
        )

    return None
