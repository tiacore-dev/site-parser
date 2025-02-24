import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from app.utils.driver import create_firefox_driver


def scroll_down(driver):
    """Плавно прокручивает страницу вниз, чтобы подгрузить динамический контент."""
    scroll_pause_time = 2  # Задержка между скроллами
    screen_height = driver.execute_script(
        "return window.innerHeight;")  # Высота окна браузера
    scroll_count = 0

    while True:
        scroll_count += 1
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)

        new_height = driver.execute_script(
            "return document.body.scrollHeight;")
        if new_height == screen_height:  # Если высота не изменилась, значит, скроллить больше нечего
            break
        screen_height = new_height

    logger.info(f"✅ Страница прокручена {scroll_count} раз(а).")


def find_element_with_retries(driver, xpath, max_attempts=5, delay=3):
    """Ищет элемент, делая несколько попыток с задержкой."""
    attempts = 0
    while attempts < max_attempts:
        try:
            element = WebDriverWait(driver, delay).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            logger.info(f"✅ Найден элемент: {xpath} (попытка {attempts+1})")
            return element.text
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
        time.sleep(5)  # Ждём начальную загрузку страницы

        logger.info("📜 Прокручиваем страницу...")
        scroll_down(driver)

        stats = {}

        stats["subscribers"] = find_element_with_retries(
            driver, "//h2[contains(text(), 'Подписчики')]/preceding-sibling::h2")
        stats["average_views"] = find_element_with_retries(
            driver, "//h2[contains(text(), 'средний охват')]/preceding-sibling::h2")
        stats["engagement_rate"] = find_element_with_retries(
            driver, "//h2[contains(text(), 'ERR')]/preceding-sibling::h2")
        stats["creation_date"] = find_element_with_retries(
            driver, "//h2[contains(text(), 'Дата создания')]/preceding-sibling::h2")
        stats["posts_count"] = find_element_with_retries(
            driver, "//h2[contains(text(), 'публикаций')]/preceding-sibling::h2")

        logger.info(f"📊 Собранные данные: {stats}")

        return {"channel_url": channel_url, "stats": stats}

    finally:
        logger.info("❎ Закрываем браузер...")
        driver.quit()
