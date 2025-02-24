import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from app.utils.driver import create_firefox_driver


def scroll_down_slowly(driver, step=500, delay=2):
    """Постепенно прокручивает страницу вниз, чтобы подгрузить все элементы."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Скроллим вниз на step пикселей
        driver.execute_script(f"window.scrollBy(0, {step});")
        time.sleep(delay)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Если высота не изменилась – значит, всё прогрузилось
        last_height = new_height
    logger.info("✅ Полностью прокрутили страницу.")


def find_element_with_retries(driver, xpath, max_attempts=5, delay=3):
    """Ищет элемент, делая несколько попыток с задержкой."""
    attempts = 0
    while attempts < max_attempts:
        try:
            element = WebDriverWait(driver, delay).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            logger.info(f"✅ Найден элемент: {xpath} (попытка {attempts+1})")
            return element.text.strip()
        except Exception:
            logger.warning(
                f"⚠ Элемент {xpath} не найден (попытка {attempts+1})")
            time.sleep(delay)
            attempts += 1
    return None


def get_tgstat_channel_stats(channel_url):
    """Парсит статистику Telegram-канала с Tgstat."""
    driver = create_firefox_driver()

    try:
        logger.info(f"🌍 Открываем страницу {channel_url}")
        driver.get(channel_url)
        time.sleep(5)  # Ждём начальную загрузку

        logger.info("📜 Прокручиваем страницу для подгрузки контента...")
        scroll_down_slowly(driver)

        stats = {}

        # Получаем данные
        stats["subscribers"] = find_element_with_retries(
            driver, "//div[contains(text(), 'подписчики')]/preceding-sibling::h2")
        stats["average_views"] = find_element_with_retries(
            driver, "//div[contains(text(), 'средний охват')]/preceding-sibling::h2")
        stats["engagement_rate"] = find_element_with_retries(
            driver, "//div[contains(text(), 'вовлеченность подписчиков (ER)')]/preceding-sibling::h2")
        stats["creation_date"] = find_element_with_retries(
            driver, "//span[contains(text(), 'канал создан')]/preceding-sibling::b")
        stats["total_posts"] = find_element_with_retries(
            driver, "//div[contains(text(), 'публикации')]/preceding-sibling::h2")
        stats["citation_index"] = find_element_with_retries(
            driver, "//div[contains(text(), 'индекс цитирования')]/preceding-sibling::h2")

        logger.info(f"📊 Собранные данные: {stats}")

        return {"channel_url": channel_url, "stats": stats}

    finally:
        logger.info("❎ Закрываем браузер...")
        driver.quit()
