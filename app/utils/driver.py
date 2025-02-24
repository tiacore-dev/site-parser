import os
from loguru import logger
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options


def create_firefox_driver():
    """Создает Firefox WebDriver в headless-режиме."""
    try:
        logger.info("Запуск драйвера Firefox...")

        options = Options()
        options.headless = True  # Headless-режим

        # Дополнительные аргументы для работы в контейнере
        # Использование RAM вместо /dev/shm
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")  # Без песочницы
        options.add_argument("--disable-gpu")  # Без GPU
        options.add_argument("--window-size=1920x1080")  # Фикс багов отрисовки

        # Окружение для headless-режима
        os.environ["MOZ_HEADLESS"] = "1"
        os.environ["DISPLAY"] = ":99"

        # Запускаем драйвер с уже установленным geckodriver (из Dockerfile)
        service = Service("/usr/local/bin/geckodriver")
        driver = webdriver.Firefox(service=service, options=options)

        logger.info("Драйвер успешно запущен!")
        return driver

    except Exception as e:
        logger.error(f"Ошибка при создании драйвера Firefox: {e}")
        raise
