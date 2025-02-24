from fastapi import APIRouter
from pydantic import BaseModel
from app.services.youtube_scraper import get_youtube_comments  # Импортируем парсер

youtube_router = APIRouter()

# Определяем модель для входных данных


class YouTubeRequest(BaseModel):
    video_url: str
    max_comments: int = 20


@youtube_router.post("/youtube/comments")
async def youtube_comments(request: YouTubeRequest):
    result = get_youtube_comments(request.video_url, request.max_comments)
    return result
