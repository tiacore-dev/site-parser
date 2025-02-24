import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from app.utils.driver import create_firefox_driver


def get_tgstat_channel_stats(channel_url):
    """Парсит статистику Telegram-канала с Tgstat."""
    driver = create_firefox_driver()

    try:
        logger.info(f"Открываем страницу канала {channel_url}")
        driver.get(channel_url)
        time.sleep(5)  # Ждём загрузку страницы

        logger.info("Ждём полную загрузку страницы...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Лог HTML страницы
        logger.info("HTML страницы после загрузки:")
        logger.info(driver.page_source[:1000])  # Выведем только часть

        # Лог текста страницы
        logger.info("Текст на странице:")
        logger.info(driver.execute_script("return document.body.innerText;"))

        stats = {}

        try:
            # Подписчики
            subscribers = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h2[contains(text(), 'Подписчики')]/preceding-sibling::h2"))
            ).text
            stats["subscribers"] = subscribers
            logger.info(f"Подписчики: {subscribers}")

        except Exception as e:
            logger.warning(f"Не удалось получить подписчиков: {e}")

        try:
            # Средний охват
            avg_views = driver.find_element(
                By.XPATH, "//h2[contains(text(), 'средний охват')]/preceding-sibling::h2"
            ).text
            stats["average_views"] = avg_views
            logger.info(f"Средний охват: {avg_views}")

        except Exception as e:
            logger.warning(f"Не удалось получить средний охват: {e}")

        try:
            # ERR (вовлеченность)
            er = driver.find_element(
                By.XPATH, "//h2[contains(text(), 'ERR')]/preceding-sibling::h2"
            ).text
            stats["engagement_rate"] = er
            logger.info(f"ERR: {er}")

        except Exception as e:
            logger.warning(f"Не удалось получить ERR: {e}")

        try:
            # Дата создания
            creation_date = driver.find_element(
                By.XPATH, "//h2[contains(text(), 'Дата создания')]/preceding-sibling::h2"
            ).text
            stats["creation_date"] = creation_date
            logger.info(f"Дата создания канала: {creation_date}")

        except Exception as e:
            logger.warning(f"Не удалось получить дату создания: {e}")

        try:
            # Количество публикаций
            posts_count = driver.find_element(
                By.XPATH, "//h2[contains(text(), 'публикаций')]/preceding-sibling::h2"
            ).text
            stats["posts_count"] = posts_count
            logger.info(f"Количество публикаций: {posts_count}")

        except Exception as e:
            logger.warning(f"Не удалось получить количество публикаций: {e}")

        return {"channel_url": channel_url, "stats": stats}

    finally:
        logger.info("Закрываем браузер...")
        driver.quit()
