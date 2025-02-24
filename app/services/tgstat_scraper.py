import time
from loguru import logger
# Импортируем Selenium Wire вместо обычного SeleniumS
from seleniumwire import webdriver


def get_tgstat_channel_stats(channel_url):
    """Парсит статистику Telegram-канала с Tgstat, перехватывая AJAX-запросы."""
    options = webdriver.FirefoxOptions()
    options.headless = True
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")  # Без песочницы
    options.add_argument("--disable-gpu")  # Без GPU
    options.add_argument("--window-size=1920x1080")  # Фикс багов отрисовки
    driver = webdriver.Firefox(options=options)

    try:
        logger.info(f"🌍 Открываем страницу {channel_url}")
        driver.get(channel_url)
        time.sleep(5)

        logger.info("📡 Перехватываем сетевые запросы...")
        for request in driver.requests:
            if "stat" in request.url and request.response:
                logger.info(f"🔍 Найден запрос к API: {request.url}")
                logger.info(
                    f"🔍 Кодировка ответа: {request.response.headers.get('Content-Type')}")
                response_encoding = request.response.encoding or 'utf-8'
                response_text = request.response.body.decode(
                    response_encoding, errors="replace")
                logger.info(f"📥 Ответ: {response_text}")
                break  # Можно обработать ответ JSON, если он в таком формате

    finally:
        logger.info("❎ Закрываем браузер...")
        driver.quit()
