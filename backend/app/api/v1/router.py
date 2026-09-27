from fastapi import APIRouter

from app.genres.router import router as genres_router
from app.movies.router import router as movies_router
from app.people.router import router as people_router
from app.reviews.router import router as reviews_router

api_router = APIRouter()

api_router.include_router(movies_router)
api_router.include_router(reviews_router)
api_router.include_router(people_router)
api_router.include_router(genres_router)
