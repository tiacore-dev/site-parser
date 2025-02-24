from .youtube_route import youtube_router
from .tgstat_route import tgstat_router
# Функция для регистрации всех маршрутов


def register_routes(app):
    app.include_router(youtube_router, prefix="/api", tags=["YouTube Scraper"])
    app.include_router(tgstat_router, prefix="/api", tags=["TGStat Scraper"])
