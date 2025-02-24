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
        time.sleep(5)

        stats = {}

        try:
            # Подписчики
            subscribers = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(text(), 'подписчики')]/preceding-sibling::h2"))
            ).text
            stats["subscribers"] = subscribers.strip()
            logger.info(f"Подписчики: {subscribers}")

            # Средний охват 1 публикации
            avg_views = driver.find_element(
                By.XPATH, "//div[contains(text(), 'средний охват')]/preceding-sibling::h2"
            ).text
            stats["average_views"] = avg_views.strip()
            logger.info(f"Средний охват: {avg_views}")

            # ERR (вовлеченность)
            engagement_rate = driver.find_element(
                By.XPATH, "//div[contains(text(), 'вовлеченность подписчиков (ER)')]/preceding-sibling::h2"
            ).text
            stats["engagement_rate"] = engagement_rate.strip()
            logger.info(f"ERR (вовлеченность): {engagement_rate}")

            # Дата создания канала
            creation_date = driver.find_element(
                By.XPATH, "//span[contains(text(), 'канал создан')]/preceding-sibling::b"
            ).text
            stats["creation_date"] = creation_date.strip()
            logger.info(f"Дата создания канала: {creation_date}")

            # Количество публикаций
            total_posts = driver.find_element(
                By.XPATH, "//div[contains(text(), 'публикации')]/preceding-sibling::h2"
            ).text
            stats["total_posts"] = total_posts.strip()
            logger.info(f"Количество публикаций: {total_posts}")

            # Индекс цитирования
            citation_index = driver.find_element(
                By.XPATH, "//div[contains(text(), 'индекс цитирования')]/preceding-sibling::h2"
            ).text
            stats["citation_index"] = citation_index.strip()
            logger.info(f"Индекс цитирования: {citation_index}")

        except Exception as e:
            logger.warning(f"Ошибка при парсинге данных: {e}")

        return {"channel_url": channel_url, "stats": stats}

    finally:
        logger.info("Закрываем браузер...")
        driver.quit()
