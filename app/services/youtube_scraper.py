import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from loguru import logger


def create_firefox_driver():
    """Создает Firefox WebDriver в headless-режиме."""
    try:
        options = Options()
        options.headless = True  # Headless-режим (без GUI)
        service = Service(GeckoDriverManager().install()
                          )  # Автоустановка драйвера
        driver = webdriver.Firefox(service=service, options=options)
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
        time.sleep(5)  # Ждем загрузки страницы

        comments = set()
        last_height = driver.execute_script(
            "return document.documentElement.scrollHeight")

        while len(comments) < max_comments:
            driver.execute_script(
                "window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)

            comments_elements = driver.find_elements(
                By.CSS_SELECTOR, "#content-text")
            for comment in comments_elements:
                if len(comments) >= max_comments:
                    break
                comments.add(comment.text)

            new_height = driver.execute_script(
                "return document.documentElement.scrollHeight")
            if new_height == last_height:
                break  # Достигнут конец страницы
            last_height = new_height

        return {"video_url": video_url, "comments": list(comments)}

    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        return {"error": str(e)}

    finally:
        driver.quit()
