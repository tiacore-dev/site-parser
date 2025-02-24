import time
from loguru import logger
from app.utils.driver import create_firefox_driver
from bs4 import BeautifulSoup


def get_tgstat_channel_stats(channel_url):
    """Парсит статистику Telegram-канала с Tgstat."""
    driver = create_firefox_driver()

    try:
        logger.info(f"🌍 Открываем страницу {channel_url}")
        driver.get(channel_url)
        time.sleep(5)

        # Прокрутка страницы
        logger.info("📜 Прокручиваем страницу для подгрузки контента...")
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)  # Даем контенту загрузиться

        # Получаем HTML после загрузки
        page_html = driver.page_source

        # Передаем HTML в BeautifulSoup
        soup = BeautifulSoup(page_html, 'lxml')

        stats = {}

        def find_stat(label):
            """Функция поиска значения по тексту."""
            tag = soup.find(lambda tag: tag.name ==
                            "div" and label in tag.text.lower())
            if tag:
                h2 = tag.find_previous_sibling("h2")
                return h2.text.strip() if h2 else None
            return None

        # Парсим нужные параметры
        stats["subscribers"] = find_stat("подписчики")
        stats["average_views"] = find_stat("средний охват")
        stats["engagement_rate"] = find_stat("вовлеченность подписчиков (er)")
        stats["total_posts"] = find_stat("публикации")
        stats["citation_index"] = find_stat("индекс цитирования")

        # Специальный парсинг для даты создания
        date_tag = soup.find(lambda tag: tag.name ==
                             "span" and "канал создан" in tag.text.lower())
        if date_tag:
            creation_date = date_tag.find_previous_sibling("b")
            stats["creation_date"] = creation_date.text.strip(
            ) if creation_date else None

        logger.info(f"📊 Собранные данные: {stats}")

        return {"channel_url": channel_url, "stats": stats}

    finally:
        logger.info("❎ Закрываем браузер...")
        driver.quit()
