import time
import json
import chardet
import gzip
import brotli
from loguru import logger
from seleniumwire import webdriver

def decode_response_body(body, headers):
    """Декодирует тело ответа, учитывая кодировку и возможное сжатие."""
    encoding = headers.get('Content-Encoding', '').lower()
    
    try:
        if encoding == 'gzip':
            body = gzip.decompress(body)
        elif encoding == 'br':
            body = brotli.decompress(body)
    except Exception as e:
        logger.warning(f"⚠ Ошибка декомпрессии ({encoding}): {e}")

    detected_encoding = chardet.detect(body)['encoding'] or 'utf-8'
    
    try:
        decoded_text = body.decode(detected_encoding, errors='replace')
    except Exception as e:
        logger.warning(f"⚠ Ошибка декодирования в {detected_encoding}: {e}")
        decoded_text = body.decode('utf-8', errors='replace')

    return decoded_text

def get_tgstat_channel_stats(channel_url):
    """Парсит статистику Telegram-канала с Tgstat, перехватывая все запросы."""
    options = webdriver.FirefoxOptions()
    options.headless = False  # Делаем видимым для тестов
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    driver = webdriver.Firefox(options=options)

    try:
        logger.info(f"🌍 Открываем страницу {channel_url}")
        driver.get(channel_url)
        time.sleep(10)  # Даем больше времени на загрузку данных

        logger.info("📡 Перехватываем сетевые запросы...")
        for request in driver.requests:
            if not request.response:
                continue
            
            url = request.url
            status = request.response.status_code
            content_type = request.response.headers.get("Content-Type", "")

            logger.info(f"🔍 Запрос: {url} (Статус: {status}, Content-Type: {content_type})")
            logger.info(f"📜 Заголовки запроса: {request.headers}")
            
            if "application/json" in content_type:
                decoded_response = decode_response_body(request.response.body, request.response.headers)
                
                if decoded_response.startswith("{") or decoded_response.startswith("["):
                    try:
                        parsed_json = json.loads(decoded_response)
                        logger.info(f"📥 JSON-ответ: {json.dumps(parsed_json, indent=4, ensure_ascii=False)}")
                        return parsed_json
                    except json.JSONDecodeError as e:
                        logger.warning(f"⚠ Ошибка разбора JSON: {e}")
                else:
                    logger.info(f"📜 Текстовый ответ (первые 500 символов): {decoded_response[:500]}")

    finally:
        logger.info("❎ Закрываем браузер...")
        driver.quit()
