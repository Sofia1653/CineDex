from sqlalchemy.ext.asyncio import AsyncSession
from app.reviews.models import DimReview
from app.reviews.schemas import ReviewCreate
from app.reviews.crud import CRUDReview

class ReviewService:
    def __init__(self, db: AsyncSession):
        self.crud = CRUDReview(db)

    async def create_review(self, review: ReviewCreate) -> DimReview:
        return await self.crud.create_review(review)

    async def get_review_by_id(self, id_review: str) -> DimReview | None:
        return await self.crud.get_review_by_id(id_review)

    async def update_review(self, id_review: str, review: ReviewCreate) -> DimReview | None:
        return await self.review_crud.update_review(id_review, review)

    async def delete_review(self, id_review: str) -> DimReview | None:
        return await self.review_crud.delete_review(id_review)

    async def list_reviews_by_movie(
        self,
        sk_movie_id: str,
    ) -> list[DimReview]:
        return await self.review_crud.list_reviews_by_movie(sk_movie_id)

    async def get_average_rating(
        self,
        sk_movie_id: str,
    ) -> float | None:
        return await self.review_crud.get_average_rating(sk_movie_id)