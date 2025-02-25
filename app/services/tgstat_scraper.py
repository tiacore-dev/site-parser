import time
import gzip
import brotli
import chardet
import json
from loguru import logger
from seleniumwire import webdriver

def decode_response_body(body, headers):
    """Декодирует тело ответа, учитывая возможное сжатие и кодировку."""
    content_encoding = headers.get("Content-Encoding", "").lower()

    try:
        if "gzip" in content_encoding:
            logger.info("🗜 Декодируем Gzip...")
            body = gzip.decompress(body)
        elif "br" in content_encoding:
            logger.info("🗜 Декодируем Brotli...")
            body = brotli.decompress(body)
    except Exception as e:
        logger.warning(f"⚠ Ошибка распаковки ({content_encoding}): {e}")

    detected_encoding = chardet.detect(body)["encoding"] or "utf-8"

    try:
        decoded_text = body.decode(detected_encoding, errors="replace")
    except Exception as e:
        logger.warning(f"⚠ Ошибка декодирования в {detected_encoding}: {e}")
        decoded_text = body.decode("utf-8", errors="replace")

    return decoded_text

def get_tgstat_channel_stats(channel_url):
    """Открывает TGStat, устанавливает куки и заголовки."""
    options = webdriver.FirefoxOptions()
    options.headless = False  # Можно поменять на True, если не нужно окно браузера
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    # Добавляем user-agent
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/122.0"
    options.set_preference("general.useragent.override", user_agent)
    options.set_preference("dom.webdriver.enabled", False)
    options.set_preference("useAutomationExtension", False)

    driver = webdriver.Firefox(options=options)

    # Отключаем navigator.webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Устанавливаем куки
    cookies = [
        {"name": "_ga", "value": "GA1.1.1637606804.1740467729", "domain": ".tgstat.ru"},
        {"name": "_gid", "value": "GA1.2.1056863450.1740467730", "domain": ".tgstat.ru"},
        {"name": "_tgstat_csrk", "value": "41ae707c15705364c526bbdeddfd9419c7c3bb05115721bab49888eac3552285a%3A2%3A%7Bi%3A0%3Bs%3A12%3A%22_tgstat_csrk%22%3Bi%3A1%3Bs%3A32%3A%229p8Dn-_kehOcJOJ0s6aQBF3G_wrZPCyX%22%3B%7D", "domain": ".tgstat.ru"},
        {"name": "cf_clearance", "value": "QRmDyAJxR7JG41wGU4OId5H1sGrYAEO2.W2JhFfSJpQ-1740476854-1.2.1.1-h9jnYfsd8Q.NL7jFLLIM6y9sQ_ZQgLrrGf2TxGrMGkrvSDHljIhBjK2VPchE1NEV3mDf3.SZ0Gjb_1bCYJgpIc10SNUe.OG.b43SFBbH143sMFTKOXhYDLqfuXB3fjs267euwvHGNULCjHVXIdQO_ycszz7B.lxrlzyQDnfr684XOSUbl8GJ_HXexGK6AKssWmUU_NfN6WmvYpTcCFIzxj_mzIENkCAO7aJUmlWF8wS1Z3Zh9w7eqA9OR3wHqHDUtEiw4FuzXJ4QoQgjM5W1j5YsFZG507HFI4MheGbBEbU", "domain": ".tgstat.ru"}
    ]

    driver.get("https://tgstat.ru")  # Загружаем сайт, чтобы можно было установить куки
    time.sleep(2)

    for cookie in cookies:
        driver.add_cookie(cookie)

    # Открываем нужную страницу
    logger.info(f"🌍 Открываем страницу {channel_url}")
    driver.get(channel_url)
    time.sleep(10)  # Даем время на загрузку всех ресурсов

    logger.info("✅ Куки установлены, страница загружена!")

    # Отключаем перехват запросов, если не нужен
    intercept_requests = False
    if intercept_requests:
        for i, request in enumerate(driver.requests):
            if request.response:
                logger.info(f"🔍 [{i}] Запрос: {request.url}")
                content_type = request.response.headers.get("Content-Type", "Unknown")
                logger.info(f"📜 Content-Type: {content_type}")

                # Получаем тело ответа
                body = request.response.body

                # Декодируем тело ответа
                decoded_text = decode_response_body(body, request.response.headers)

                # Если это JSON, логируем красиво
                if "application/json" in content_type:
                    try:
                        parsed_json = json.loads(decoded_text)
                        logger.info(f"📥 JSON-ответ:\n{json.dumps(parsed_json, indent=4, ensure_ascii=False)}")
                    except json.JSONDecodeError:
                        logger.warning("⚠ JSON-ответ поврежден, выводим как текст.")
                        logger.info(f"📜 Текстовый ответ (первые 1000 символов): {decoded_text[:1000]}")
                else:
                    logger.info(f"📜 Текстовый ответ (первые 1000 символов): {decoded_text[:1000]}")

    finally:
        logger.info("❎ Закрываем браузер...")
        driver.quit()

