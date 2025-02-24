import os
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()


class Settings:
    INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")  # Логин
    INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")  # Пароль
