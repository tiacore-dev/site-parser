from fastapi import FastAPI
from app.logger import setup_logger
from app.routes import register_routes
# from app.config import Settings


def create_app() -> FastAPI:
    app = FastAPI()

    # app.state.settings = Settings()
   # Конфигурация Tortoise ORM

    setup_logger()
    # Регистрация маршрутов
    register_routes(app)

    return app
