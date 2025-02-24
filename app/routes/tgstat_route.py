from fastapi import APIRouter
from pydantic import BaseModel
from app.services.tgstat_scraper import get_tgstat_channel_stats  # Импортируем парсер

tgstat_router = APIRouter()

# Определяем модель для входных данных


class TGStatRequest(BaseModel):
    channel_url: str


@tgstat_router.post("/tgstat/stats")
async def tgstat_stats(request: TGStatRequest):
    result = get_tgstat_channel_stats(request.channel_url)
    return result
