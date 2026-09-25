from sqlalchemy.ext.asyncio import AsyncSession

from app.reviews.crud import CRUDReview
from app.reviews.models import MovieReview
from app.reviews.schemas import MovieReviewCreate, MovieReviewUpdate


class ReviewService:
    def __init__(self, db: AsyncSession):
        self.crud = CRUDReview(db)

    async def create_review(self, sk_movie_id: str, review: MovieReviewCreate) -> MovieReview:
        return await self.crud.create_review(sk_movie_id, review)

    async def get_review_by_id(self, sk_movie_review_id: str) -> MovieReview | None:
        return await self.crud.get_review_by_id(sk_movie_review_id)

    async def update_review(
        self,
        sk_movie_review_id: str,
        review: MovieReviewUpdate,
    ) -> MovieReview | None:
        return await self.crud.update_review(sk_movie_review_id, review)

    async def delete_review(self, sk_movie_review_id: str) -> MovieReview | None:
        return await self.crud.delete_review(sk_movie_review_id)

    async def list_reviews_by_movie(
        self,
        sk_movie_id: str,
        page: int = 1,
        size: int = 50,
    ) -> dict[str, object]:
        reviews, total = await self.crud.list_reviews_by_movie(
            sk_movie_id,
            offset=(page - 1) * size,
            limit=size,
        )

        return {
            "items": reviews,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
        }

    async def get_review_summary(self, sk_movie_id: str) -> dict[str, object] | None:
        return await self.crud.get_review_summary(sk_movie_id)
