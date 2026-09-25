from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.people.schemas import (
    PeopleListResponse,
    PeopleResponse,
    PersonMovieListResponse,
)
from app.people.services import PeopleService

router = APIRouter(
    prefix="/people",
    tags=["people"],
)


def get_people_service(
    db: AsyncSession = Depends(get_db),
) -> PeopleService:
    return PeopleService(db)


@router.get(
    "",
    response_model=PeopleListResponse,
)
async def list_people(
    nome_pessoa: str | None = Query(default=None),
    tipo_pessoa: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    service: PeopleService = Depends(get_people_service),
):
    return await service.list_people(
        nome_pessoa=nome_pessoa,
        tipo_pessoa=tipo_pessoa,
        page=page,
        size=size,
    )


@router.get(
    "/{sk_person_id}",
    response_model=PeopleResponse,
)
async def get_person(
    sk_person_id: str,
    service: PeopleService = Depends(get_people_service),
):
    person = await service.get_person_by_id(sk_person_id)

    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada",
        )

    return person


@router.get(
    "/{sk_person_id}/movies",
    response_model=PersonMovieListResponse,
)
async def get_person_movies(
    sk_person_id: str,
    service: PeopleService = Depends(get_people_service),
):
    person = await service.get_person_by_id(sk_person_id)

    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada",
        )

    return await service.get_movies_by_person(sk_person_id)
