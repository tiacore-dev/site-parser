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

        # Прокручиваем страницу вниз, чтобы прогрузился весь контент
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Даём время на подгрузку

        stats = {}

        try:
            # Подписчики
            subscribers = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(text(), 'подписчики')]/preceding-sibling::h2"))
            ).text
            stats["subscribers"] = subscribers.strip()
            logger.info(f"Подписчики: {subscribers}")

        except Exception as e:
            logger.warning(f"Не удалось получить подписчиков: {e}")

        try:
            # Средний охват 1 публикации
            avg_views = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(text(), 'средний охват')]/preceding-sibling::h2"))
            ).text
            stats["average_views"] = avg_views.strip()
            logger.info(f"Средний охват: {avg_views}")

        except Exception as e:
            logger.warning(f"Не удалось получить средний охват: {e}")

        try:
            # ERR (вовлеченность)
            engagement_rate = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(text(), 'вовлеченность подписчиков (ER)')]/preceding-sibling::h2"))
            ).text
            stats["engagement_rate"] = engagement_rate.strip()
            logger.info(f"ERR (вовлеченность): {engagement_rate}")

        except Exception as e:
            logger.warning(f"Не удалось получить ERR: {e}")

        try:
            # Дата создания канала
            creation_date = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[contains(text(), 'канал создан')]/preceding-sibling::b"))
            ).text
            stats["creation_date"] = creation_date.strip()
            logger.info(f"Дата создания канала: {creation_date}")

        except Exception as e:
            logger.warning(f"Не удалось получить дату создания: {e}")

        try:
            # Количество публикаций
            total_posts = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(text(), 'публикации')]/preceding-sibling::h2"))
            ).text
            stats["total_posts"] = total_posts.strip()
            logger.info(f"Количество публикаций: {total_posts}")

        except Exception as e:
            logger.warning(f"Не удалось получить количество публикаций: {e}")

        try:
            # Индекс цитирования
            citation_index = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(text(), 'индекс цитирования')]/preceding-sibling::h2"))
            ).text
            stats["citation_index"] = citation_index.strip()
            logger.info(f"Индекс цитирования: {citation_index}")

        except Exception as e:
            logger.warning(f"Не удалось получить индекс цитирования: {e}")

        return {"channel_url": channel_url, "stats": stats}

    finally:
        logger.info("Закрываем браузер...")
        driver.quit()
