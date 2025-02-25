import time
import json
import gzip
import brotli
import chardet
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from app.utils.driver import create_firefox_driver


# --- ФУНКЦИЯ ДЛЯ РАСПАКОВКИ ДАННЫХ ---
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


# --- ФУНКЦИЯ ДЛЯ ПОЛУЧЕНИЯ СТАТИСТИКИ ---
def get_tgstat_channel_stats(channel_url):
    """Парсит статистику Telegram-канала с Tgstat, устанавливает куки и заголовки."""
    driver = create_firefox_driver()
    
    try:
        logger.info(f"🌍 Открываем TGStat и устанавливаем куки...")

        # Открываем TGStat для установки кук
        driver.get("https://tgstat.ru")
        time.sleep(2)

        # Добавляем куки (скопированные вручную)
        cookies = [
            {"name": "_ga", "value": "GA1.1.1637606804.1740467729", "domain": ".tgstat.ru"},
            {"name": "_gid", "value": "GA1.2.1056863450.1740467730", "domain": ".tgstat.ru"},
            {"name": "_tgstat_csrk", "value": "41ae707c15705364c526bbdeddfd9419c7c3bb05115721bab49888eac3552285a%3A2%3A%7Bi%3A0%3Bs%3A12%3A%22_tgstat_csrk%22%3Bi%3A1%3Bs%3A32%3A%229p8Dn-_kehOcJOJ0s6aQBF3G_wrZPCyX%22%3B%7D", "domain": ".tgstat.ru"},
            {"name": "cf_clearance", "value": "QRmDyAJxR7JG41wGU4OId5H1sGrYAEO2.W2JhFfSJpQ-1740476854-1.2.1.1-h9jnYfsd8Q.NL7jFLLIM6y9sQ_ZQgLrrGf2TxGrMGkrvSDHljIhBjK2VPchE1NEV3mDf3.SZ0Gjb_1bCYJgpIc10SNUe.OG.b43SFBbH143sMFTKOXhYDLqfuXB3fjs267euwvHGNULCjHVXIdQO_ycszz7B.lxrlzyQDnfr684XOSUbl8GJ_HXexGK6AKssWmUU_NfN6WmvYpTcCFIzxj_mzIENkCAO7aJUmlWF8wS1Z3Zh9w7eqA9OR3wHqHDUtEiw4FuzXJ4QoQgjM5W1j5YsFZG507HFI4MheGbBEbU", "domain": ".tgstat.ru"}
        ]

        for cookie in cookies:
            driver.add_cookie(cookie)

        logger.info("✅ Куки установлены, переходим на страницу канала...")
        driver.get(channel_url)
        time.sleep(5)

        # Прокручиваем страницу вниз, чтобы прогрузился весь контент
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        stats = {}

        def get_stat(xpath, stat_name):
            """Безопасно парсит элемент по XPATH."""
            try:
                element = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                stats[stat_name] = element.text.strip()
                logger.info(f"{stat_name}: {stats[stat_name]}")
            except Exception as e:
                logger.warning(f"❌ Ошибка парсинга {stat_name}: {e}")

        # --- СБОР СТАТИСТИКИ ---
        get_stat("//div[contains(text(), 'подписчики')]/preceding-sibling::h2", "subscribers")
        get_stat("//div[contains(text(), 'средний охват')]/preceding-sibling::h2", "average_views")
        get_stat("//div[contains(text(), 'вовлеченность подписчиков (ER)')]/preceding-sibling::h2", "engagement_rate")
        get_stat("//span[contains(text(), 'канал создан')]/preceding-sibling::b", "creation_date")
        get_stat("//div[contains(text(), 'публикации')]/preceding-sibling::h2", "total_posts")
        get_stat("//div[contains(text(), 'индекс цитирования')]/preceding-sibling::h2", "citation_index")

        return {"channel_url": channel_url, "stats": stats}

    except Exception as e:
        logger.error(f"⚠ Критическая ошибка при парсинге: {e}")
        return {"channel_url": channel_url, "error": str(e)}

    finally:
        logger.info("❎ Закрываем браузер...")
        driver.quit()

