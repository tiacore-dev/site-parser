import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from app.utils.driver import create_firefox_driver


def get_youtube_comments(video_url, max_comments=20):
    """Парсит комментарии с YouTube без API."""
    driver = create_firefox_driver()
    try:
        logger.info(f"Открываем страницу {video_url}")
        driver.get(video_url)

        time.sleep(5)  # Ждем загрузки страницы

        # Проверяем, появился ли контейнер комментариев
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#comments"))
            )
            logger.info("Контейнер с комментариями найден!")
        except Exception as e:
            logger.warning(
                f"Контейнер с комментариями не найден! Возможно, YouTube блокирует запрос. error message: {e}")
            return {"error": "Контейнер с комментариями не найден"}

        comments = set()
        last_height = driver.execute_script(
            "return document.documentElement.scrollHeight")

        logger.info("Начинаем прокрутку страницы для загрузки комментариев...")

        while len(comments) < max_comments:
            logger.info(
                f"Прокручиваем страницу вниз... ({len(comments)}/{max_comments})")

            # Скроллим с имитацией нажатия клавиши "End"
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

            # Ожидание загрузки новых комментариев
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#content-text"))
                )
            except Exception as e:
                logger.warning(
                    f"Новые комментарии не загрузились! Error message: {e}")

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
