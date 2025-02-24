import time
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.utils.driver import create_firefox_driver


def get_tgstat_channel_stats(channel_url):
    """Парсит статистику Telegram-канала с Tgstat, имитируя взаимодействие с сайтом."""
    driver = create_firefox_driver()

    try:
        logger.info(f"🌍 Открываем страницу {channel_url}")
        driver.get(channel_url)
        time.sleep(5)

        # Прокрутка страницы вниз несколько раз для подгрузки данных
        logger.info("📜 Прокручиваем страницу для подгрузки контента...")
        for _ in range(3):
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Пробуем кликать по вкладкам, если они есть
        def click_tab(tab_text):
            try:
                tab = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//div[contains(text(), '{tab_text}')]"))
                )
                tab.click()
                logger.info(f"✅ Кликнули по вкладке: {tab_text}")
                time.sleep(2)  # Даём контенту загрузиться
            except Exception as e:
                logger.warning(
                    f"⚠ Не удалось кликнуть по вкладке '{tab_text}': {e}")

        click_tab("Подписчики")
        click_tab("Индекс цитирования")
        click_tab("Охваты публикаций")

        # Теперь пробуем снова получить данные
        stats = {}

        def find_stat(label, xpath):
            """Функция поиска значения с логами."""
            try:
                logger.info(f"🔍 Ищем '{label}'...")
                value = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                ).text.strip()
                logger.info(f"✅ Найдено '{label}': {value}")
                return value
            except Exception as e:
                logger.warning(f"⚠ Не удалось найти '{label}': {e}")
                return None

        stats["subscribers"] = find_stat(
            "Подписчики", "//h2[contains(text(), 'подписчики')]/preceding-sibling::h2")
        stats["average_views"] = find_stat(
            "Средний охват", "//h2[contains(text(), 'средний охват')]/preceding-sibling::h2")
        stats["engagement_rate"] = find_stat(
            "Вовлеченность", "//h2[contains(text(), 'вовлеченность подписчиков (ER)')]/preceding-sibling::h2")
        stats["total_posts"] = find_stat(
            "Публикации", "//h2[contains(text(), 'публикации')]/preceding-sibling::h2")
        stats["citation_index"] = find_stat(
            "Индекс цитирования", "//h2[contains(text(), 'индекс цитирования')]/preceding-sibling::h2")

        logger.info(f"📊 Собранные данные: {stats}")
        return {"channel_url": channel_url, "stats": stats}

    finally:
        logger.info("❎ Закрываем браузер...")
        driver.quit()
