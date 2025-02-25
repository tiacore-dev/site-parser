import time
import gzip
import brotli
import chardet
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
                logger.info(f"🔍 Атрибуты response: {dir(request.response)}")
                body = request.response.body
                with open("tgstat_raw_response.bin", "wb") as f:
                    f.write(body)
                logger.info("📂 Сырые данные сохранены в файл tgstat_raw_response.bin")
                logger.info(f"🔍 HEX-дамп первых 100 байтов: {body[:100].hex()}")

                content_encoding = request.response.headers.get("Content-Encoding", "")
                if "charset=" in content_encoding:
                    response_encoding = content_encoding.split("charset=")[-1]
                else:
                    try:
                        if "gzip" in content_encoding:
                            logger.info("🗜 Попробуем ещё раз явно распаковать Gzip...")
                            body = gzip.decompress(body)
                        elif "br" in content_encoding:
                            logger.info("🗜 Попробуем ещё раз явно распаковать Brotli...")
                            body = brotli.decompress(body)
                    except Exception as e:
                        logger.warning(f"⚠ Ошибка распаковки: {e}")
                    detected = chardet.detect(body)
                    response_encoding = detected["encoding"] if detected["encoding"] else "utf-8"
                    logger.info(f"📊 Определённая кодировка: {response_encoding}")

                    response_encoding = detected["encoding"] if detected["encoding"] else "utf-8"

                try:
                    response_text = body.decode(response_encoding, errors="replace")
                    logger.info(f"📥 Декодированный ответ: {response_text[:1000]}")  # Только первые 1000 символов, чтобы не заспамить логи
                except Exception as e:
                    logger.warning(f"⚠ Ошибка декодирования: {e}")

                logger.info(f"📥 Декодированный ответ: {response_text}")

                break  # Можно обработать ответ JSON, если он в таком формате

    finally:
        logger.info("❎ Закрываем браузер...")
        driver.quit()
