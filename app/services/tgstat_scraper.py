import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
from app.utils.driver import create_firefox_driver


def retry_find_element(driver, by, value, retries=5, delay=3):
    """Функция с ретраями: пытается найти элемент несколько раз."""
    attempt = 0
    start_time = time.time()

    while attempt < retries:
        try:
            element = WebDriverWait(driver, delay).until(
                EC.presence_of_element_located((by, value))
            )
            elapsed_time = time.time() - start_time
            logger.info(
                f"Элемент найден на {attempt + 1}-й попытке (за {elapsed_time:.2f} сек).")
            return element
        except Exception:
            logger.warning(
                f"Попытка {attempt + 1}/{retries}: элемент не найден. Ждём {delay} сек...")
            time.sleep(delay)
            attempt += 1

    logger.error(f"Не удалось найти элемент после {retries} попыток.")
    return None


def get_tgstat_channel_stats(channel_url):
    """Парсит статистику Telegram-канала с Tgstat."""
    driver = create_firefox_driver()

    try:
        logger.info(f"Открываем страницу канала {channel_url}")
        driver.get(channel_url)

        logger.info("Ждём полную загрузку страницы...")
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script(
                "return document.readyState") == "complete"
        )

        logger.info("Ждём 5 секунд на прогрузку динамического контента...")
        time.sleep(5)  # Ждём дополнительную загрузку данных

        # Лог HTML страницы
        logger.info("HTML страницы после загрузки:")
        logger.info(driver.page_source[:1000])  # Выведем только часть

        stats = {}

        # Подписчики
        element = retry_find_element(
            driver, By.XPATH, "//h2[contains(text(), 'Подписчики')]/preceding-sibling::h2")
        if element:
            stats["subscribers"] = element.text
            logger.info(f"Подписчики: {element.text}")
        else:
            logger.warning("Не удалось получить подписчиков")

        # Средний охват
        element = retry_find_element(
            driver, By.XPATH, "//h2[contains(text(), 'средний охват')]/preceding-sibling::h2")
        if element:
            stats["average_views"] = element.text
            logger.info(f"Средний охват: {element.text}")
        else:
            logger.warning("Не удалось получить средний охват")

        # ERR (вовлеченность)
        element = retry_find_element(
            driver, By.XPATH, "//h2[contains(text(), 'ERR')]/preceding-sibling::h2")
        if element:
            stats["engagement_rate"] = element.text
            logger.info(f"ERR: {element.text}")
        else:
            logger.warning("Не удалось получить ERR")

        # Дата создания
        element = retry_find_element(
            driver, By.XPATH, "//h2[contains(text(), 'Дата создания')]/preceding-sibling::h2")
        if element:
            stats["creation_date"] = element.text
            logger.info(f"Дата создания канала: {element.text}")
        else:
            logger.warning("Не удалось получить дату создания")

        # Количество публикаций
        element = retry_find_element(
            driver, By.XPATH, "//h2[contains(text(), 'публикаций')]/preceding-sibling::h2")
        if element:
            stats["posts_count"] = element.text
            logger.info(f"Количество публикаций: {element.text}")
        else:
            logger.warning("Не удалось получить количество публикаций")

        return {"channel_url": channel_url, "stats": stats}

    finally:
        logger.info("Закрываем браузер...")
        driver.quit()
