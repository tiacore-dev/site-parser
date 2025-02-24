import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from app.utils.driver import create_firefox_driver


def get_tgstat_comments(post_url, max_comments=20):
    """Парсит комментарии с поста Tgstat."""
    driver = create_firefox_driver()
    try:
        logger.info(f"Открываем страницу {post_url}")
        driver.get(post_url)
        time.sleep(5)

        # Проверяем, есть ли блок комментариев
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".comments"))
            )
            logger.info("Контейнер с комментариями найден!")
        except Exception as e:
            logger.warning(
                f"Контейнер с комментариями не найден! Возможно, комментарии отключены. Error message: {e}")
            return {"error": "Контейнер с комментариями не найден"}

        comments = set()
        last_height = driver.execute_script(
            "return document.documentElement.scrollHeight")

        logger.info("Начинаем прокрутку комментариев...")

        while len(comments) < max_comments:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".comment-item"))
                )
            except Exception as e:
                logger.warning(
                    f"Новые комментарии не подгружаются! Error message: {e}")

            comment_elements = driver.find_elements(
                By.CSS_SELECTOR, ".comment-item .text")

            if not comment_elements:
                logger.warning(
                    "Комментарии не найдены! Возможно, пост закрыт.")
                break

            for comment in comment_elements:
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

        return {"post_url": post_url, "comments": list(comments)}

    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        return {"error": str(e)}

    finally:
        logger.info("Закрываем браузер...")
        driver.quit()
