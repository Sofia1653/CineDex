from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.reviews.schemas import ReviewCreate
from app.reviews.models import DimReview

class CRUDReview:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_review(self, review: ReviewCreate) -> DimReview:
        db_review = DimReview(**review.model_dump())
        self.db.add(db_review)
        await self.db.commit()
        await self.db.refresh(db_review)
        return db_review

    async def get_review_by_id(self, id_review: str) -> DimReview | None:
        return await self.db.get(DimReview, id_review)

    async def update_review(self, id_review: str, review: ReviewCreate) -> DimReview | None:
        db_review = await self.get_review_by_id(id_review)
        if db_review is None:
            return None

        update_data = review.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_review, field, value)

        await self.db.commit()
        await self.db.refresh(db_review)
        return db_review

    async def delete_review(self, id_review: str) -> DimReview | None:
        db_review = await self.get_review_by_id(id_review)
        if db_review is None:
            return None

        await self.db.delete(db_review)
        await self.db.commit()
        return db_review

    async def list_reviews_by_movie(
        self,
        sk_movie_id: str,
    ) -> list[DimReview]:
        query = (
            select(DimReview)
            .where(DimReview.sk_movie_id == sk_movie_id)
            .order_by(DimReview.created_at.desc())
        )

        result = await self.db.execute(query)

        return list(result.scalars().all())

    async def get_average_rating(
        self,
        sk_movie_id: str,
    ) -> float | None:
        query = select(func.avg(DimReview.nota)).where(
            DimReview.sk_movie_id == sk_movie_id
        )

        result = await self.db.execute(query)
        average = result.scalar_one_or_none()

        if average is None:
            return None

        return round(float(average), 2)