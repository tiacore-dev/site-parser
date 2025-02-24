import time
from loguru import logger
from bs4 import BeautifulSoup
from app.utils.driver import create_firefox_driver


def get_tgstat_channel_stats(channel_url):
    """Парсит статистику Telegram-канала с Tgstat."""
    driver = create_firefox_driver()

    try:
        logger.info(f"🌍 Открываем страницу {channel_url}")
        driver.get(channel_url)
        time.sleep(5)

        # Прокрутка страницы вниз несколько раз для подгрузки данных
        logger.info("📜 Прокручиваем страницу для подгрузки контента...")
        for _ in range(3):  # Скроллим 3 раза, чтобы наверняка прогрузить
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        logger.info("✅ Закончили скроллинг, получаем HTML...")

        # Получаем HTML после загрузки
        page_html = driver.page_source

        # Логируем первые 2000 символов, чтобы убедиться, что контент есть
        logger.info(f"🔍 HTML страницы (фрагмент): {page_html[:2000]}")

        # Передаем HTML в BeautifulSoup
        soup = BeautifulSoup(page_html, "html.parser")

        stats = {}

        def find_stat(label):
            """Функция поиска значения по тексту."""
            logger.info(f"🔍 Ищем '{label}' в HTML...")
            tag = soup.find(lambda tag: tag.name ==
                            "div" and label.lower() in tag.text.lower())

            if tag:
                h2 = tag.find_previous_sibling("h2")
                if h2:
                    logger.info(f"✅ Найден '{label}': {h2.text.strip()}")
                    return h2.text.strip()
                else:
                    logger.warning(
                        f"⚠ Текст найден, но предшествующий <h2> отсутствует: {tag.text.strip()}")
            else:
                logger.warning(f"⚠ Не найден '{label}' в HTML!")

            return None

        # Парсим нужные параметры
        stats["subscribers"] = find_stat("подписчики")
        stats["average_views"] = find_stat("средний охват")
        stats["engagement_rate"] = find_stat("вовлеченность подписчиков (er)")
        stats["total_posts"] = find_stat("публикации")
        stats["citation_index"] = find_stat("индекс цитирования")

        # Специальный парсинг для даты создания
        logger.info("🔍 Ищем дату создания канала...")
        date_tag = soup.find(lambda tag: tag.name ==
                             "span" and "канал создан" in tag.text.lower())
        if date_tag:
            creation_date = date_tag.find_previous_sibling("b")
            if creation_date:
                stats["creation_date"] = creation_date.text.strip()
                logger.info(
                    f"✅ Дата создания канала: {creation_date.text.strip()}")
            else:
                logger.warning("⚠ Не найден тег <b> перед датой создания!")
        else:
            logger.warning("⚠ Не найдена дата создания!")

        logger.info(f"📊 Собранные данные: {stats}")

        return {"channel_url": channel_url, "stats": stats}

    finally:
        logger.info("❎ Закрываем браузер...")
        driver.quit()
