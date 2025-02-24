from fastapi import APIRouter
from pydantic import BaseModel
from app.services.tgstat_scraper import get_tgstat_channel_stats  # Импортируем парсер
from app.services.tgstat_requests import get_tgstat_channel_stats_requests

tgstat_router = APIRouter()

# Определяем модель для входных данных


class TGStatRequest(BaseModel):
    channel_url: str


@tgstat_router.post("/tgstat/stats/selenium")
async def tgstat_stats_selenium(request: TGStatRequest):
    result = get_tgstat_channel_stats(request.channel_url)
    return result


@tgstat_router.post("/tgstat/stats/requests")
async def tgstat_stats_requests(request: TGStatRequest):
    result = get_tgstat_channel_stats_requests(request.channel_url)
    return result
