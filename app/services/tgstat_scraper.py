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
            # Охват (средний)
            avg_views = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(text(), 'Средний охват')]/following-sibling::div"))
            ).text
            stats["average_views"] = avg_views
            logger.info(f"Средний охват: {avg_views}")

            # ER (вовлеченность)
            er = driver.find_element(
                By.XPATH, "//div[contains(text(), 'ER')]/following-sibling::div").text
            stats["engagement_rate"] = er
            logger.info(f"ER: {er}")

            # Количество подписчиков
            subscribers = driver.find_element(
                By.XPATH, "//div[contains(text(), 'Подписчики')]/following-sibling::div").text
            stats["subscribers"] = subscribers
            logger.info(f"Подписчики: {subscribers}")

            # Дата создания
            creation_date = driver.find_element(
                By.XPATH, "//div[contains(text(), 'Создан')]/following-sibling::div").text
            stats["creation_date"] = creation_date
            logger.info(f"Дата создания: {creation_date}")

        except Exception as e:
            logger.warning(f"Ошибка при парсинге данных: {e}")

        return {"channel_url": channel_url, "stats": stats}

    finally:
        logger.info("Закрываем браузер...")
        driver.quit()
