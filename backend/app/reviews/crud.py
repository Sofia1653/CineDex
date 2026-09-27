from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import generate_surrogate_key
from app.reviews.models import DimReview, MovieReview
from app.reviews.schemas import MovieReviewCreate, MovieReviewUpdate


class CRUDReview:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def recalculate_summary(self, sk_movie_id: str) -> DimReview | None:
        """Recalcula o resumo consolidado do filme a partir das avaliações reais.

        `dim_reviews` alimenta o card do catálogo, o preview e a página de
        detalhe. Sem esta recomputação a nota e a quantidade de avaliações ficam
        desatualizadas depois que o usuário cria, edita ou remove uma avaliação.
        """
        total, media = (
            await self.db.execute(
                select(
                    func.count(MovieReview.sk_movie_review_id),
                    func.avg(MovieReview.nota),
                ).where(MovieReview.sk_movie_id == sk_movie_id)
            )
        ).one()

        summary = (
            await self.db.execute(select(DimReview).where(DimReview.sk_movie_id == sk_movie_id))
        ).scalar_one_or_none()

        if not total:
            # Sem avaliações o filme não deve exibir nota nem contagem.
            if summary is not None:
                summary.qtd_avaliacoes_usuarios = 0
                summary.nota_media_usuarios = None
                await self.db.flush()
            return summary

        nota_media = round(float(media), 2) if media is not None else None

        if summary is None:
            summary = DimReview(
                sk_review_id=generate_surrogate_key(),
                sk_movie_id=sk_movie_id,
                qtd_avaliacoes_usuarios=int(total),
                nota_media_usuarios=nota_media,
            )
            self.db.add(summary)
        else:
            summary.qtd_avaliacoes_usuarios = int(total)
            summary.nota_media_usuarios = nota_media

        await self.db.flush()

        return summary

    async def create_review(self, sk_movie_id: str, review: MovieReviewCreate) -> MovieReview:
        db_review = MovieReview(sk_movie_id=sk_movie_id, **review.model_dump())
        self.db.add(db_review)
        await self.db.flush()
        await self.recalculate_summary(sk_movie_id)
        await self.db.commit()
        await self.db.refresh(db_review)
        return db_review

    async def get_review_by_id(self, sk_movie_review_id: str) -> MovieReview | None:
        return await self.db.get(MovieReview, sk_movie_review_id)

    async def update_review(
        self,
        sk_movie_review_id: str,
        review: MovieReviewUpdate,
    ) -> MovieReview | None:
        db_review = await self.get_review_by_id(sk_movie_review_id)
        if db_review is None:
            return None

        sk_movie_id = db_review.sk_movie_id

        for field, value in review.model_dump(exclude_unset=True).items():
            setattr(db_review, field, value)

        await self.db.flush()
        await self.recalculate_summary(sk_movie_id)
        await self.db.commit()
        await self.db.refresh(db_review)
        return db_review

    async def delete_review(self, sk_movie_review_id: str) -> MovieReview | None:
        db_review = await self.get_review_by_id(sk_movie_review_id)
        if db_review is None:
            return None

        sk_movie_id = db_review.sk_movie_id

        await self.db.delete(db_review)
        await self.db.flush()
        await self.recalculate_summary(sk_movie_id)
        await self.db.commit()
        return db_review

    async def list_reviews_by_movie(
        self,
        sk_movie_id: str,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[MovieReview], int]:
        filters = MovieReview.sk_movie_id == sk_movie_id

        total = (
            await self.db.scalar(select(func.count()).select_from(MovieReview).where(filters))
        ) or 0

        query = (
            select(MovieReview)
            .where(filters)
            .order_by(MovieReview.created_at.desc(), MovieReview.sk_movie_review_id.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(query)

        return list(result.scalars().all()), total

    async def get_review_summary(self, sk_movie_id: str) -> dict[str, object] | None:
        """Resume as avaliações do filme sem alterar o banco.

        As avaliações individuais em `movie_reviews` são a fonte da verdade. Se o
        filme ainda não tiver nenhuma, usa o resumo consolidado pré-carregado.
        """
        query = select(
            func.count(MovieReview.sk_movie_review_id),
            func.avg(MovieReview.nota),
        ).where(MovieReview.sk_movie_id == sk_movie_id)

        qtd_avaliacoes, nota_media = (await self.db.execute(query)).one()

        if qtd_avaliacoes:
            media = round(float(nota_media), 2) if nota_media is not None else None
            return {
                "sk_movie_id": sk_movie_id,
                "qtd_avaliacoes_usuarios": int(qtd_avaliacoes),
                "nota_media_usuarios": media,
            }

        summary = await self.find_summary(sk_movie_id)
        if summary is None or not summary.qtd_avaliacoes_usuarios:
            return None

        return {
            "sk_review_id": summary.sk_review_id,
            "sk_movie_id": summary.sk_movie_id,
            "qtd_avaliacoes_usuarios": summary.qtd_avaliacoes_usuarios or 0,
            "nota_media_usuarios": summary.nota_media_usuarios,
        }

    async def find_summary(self, sk_movie_id: str) -> DimReview | None:
        query = select(DimReview).where(DimReview.sk_movie_id == sk_movie_id)
        return (await self.db.execute(query)).scalar_one_or_none()
