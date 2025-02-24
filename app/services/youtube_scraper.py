import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from loguru import logger


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


def get_youtube_comments(video_url, max_comments=20):
    """Парсит комментарии с YouTube без API."""
    driver = create_firefox_driver()
    try:
        logger.info(f"Открываем страницу {video_url}")
        driver.get(video_url)

        # Проверяем, действительно ли открыта страница
        current_url = driver.current_url
        if "consent" in current_url:
            logger.warning("YouTube требует подтверждения cookies!")
            return {"error": "YouTube требует подтверждения cookies"}

        time.sleep(5)  # Ждем загрузки страницы

        comments = set()
        last_height = driver.execute_script(
            "return document.documentElement.scrollHeight")

        logger.info("Начинаем прокрутку страницы для загрузки комментариев...")

        while len(comments) < max_comments:
            logger.info(
                f"Прокручиваем страницу вниз... ({len(comments)}/{max_comments})")

            driver.execute_script(
                "window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)

            comments_elements = driver.find_elements(
                By.CSS_SELECTOR, "#content-text")

            if not comments_elements:
                logger.warning(
                    "Комментарии не найдены! Возможно, они отключены или видео закрыто.")
                break

            for comment in comments_elements:
                text = comment.text.strip()
                if text and text not in comments:
                    comments.add(text)
                    logger.debug(f"Добавлен комментарий: {text[:50]}...")

                if len(comments) >= max_comments:
                    logger.info(
                        "Достигнуто максимальное количество комментариев.")
                    break

            new_height = driver.execute_script(
                "return document.documentElement.scrollHeight")
            if new_height == last_height:
                logger.info(
                    "Достигнут конец страницы, больше комментариев нет.")
                break
            last_height = new_height

        if not comments:
            logger.warning("Не удалось собрать ни одного комментария!")

        return {"video_url": video_url, "comments": list(comments)}

    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        return {"error": str(e)}

    finally:
        logger.info("Закрываем браузер...")
        driver.quit()
