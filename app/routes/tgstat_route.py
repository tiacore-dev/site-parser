from fastapi import APIRouter
from pydantic import BaseModel
from app.services.tgstat_scraper import get_tgstat_comments  # Импортируем парсер

tgstat_router = APIRouter()

# Определяем модель для входных данных


class TGStatRequest(BaseModel):
    post_url: str
    max_comments: int = 20


@tgstat_router.post("/tgstat/comments")
async def tgstat_comments(request: TGStatRequest):
    result = get_tgstat_comments(request.post_url, request.max_comments)
    return result
