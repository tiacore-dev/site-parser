import requests
from bs4 import BeautifulSoup
from loguru import logger

# Заголовки для имитации браузера
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
}


def fetch_tgstat_html(url):
    """Запрашивает HTML страницы TGStat через requests."""
    try:
        logger.info(f"Отправляем GET-запрос на {url}...")
        response = requests.get(url, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            logger.info("✅ Успешно получили HTML-страницу.")
            return response.text
        else:
            logger.warning(f"⚠ Ошибка запроса: {response.status_code}")
            return None
    except requests.RequestException as e:
        logger.error(f"❌ Ошибка при запросе: {e}")
        return None


def parse_tgstat(html):
    """Парсит HTML страницы TGStat и извлекает ключевые метрики."""
    soup = BeautifulSoup(html, "html.parser")
    stats = {}

    try:
        # Подписчики
        subscribers = soup.find(string="ПОДПИСЧИКИ")
        if subscribers:
            stats["subscribers"] = subscribers.find_next("h2").text.strip()
            logger.info(f"📊 Подписчики: {stats['subscribers']}")

        # Средний охват
        avg_views = soup.find(string="СРЕДНИЙ ОХВАТ")
        if avg_views:
            stats["average_views"] = avg_views.find_next("h2").text.strip()
            logger.info(f"📊 Средний охват: {stats['average_views']}")

        # ERR (вовлеченность)
        err = soup.find(string="ВОВЛЕЧЕННОСТЬ ПОДПИСЧИКОВ (ERR)")
        if err:
            stats["engagement_rate"] = err.find_next("h2").text.strip()
            logger.info(f"📊 ERR: {stats['engagement_rate']}")

        # Дата создания
        creation_date = soup.find(string="канал создан")
        if creation_date:
            stats["creation_date"] = creation_date.find_next("h2").text.strip()
            logger.info(f"📊 Дата создания: {stats['creation_date']}")

        # Количество публикаций
        posts_count = soup.find(string="ПУБЛИКАЦИИ")
        if posts_count:
            stats["posts_count"] = posts_count.find_next("h2").text.strip()
            logger.info(f"📊 Количество публикаций: {stats['posts_count']}")

    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге: {e}")

    return stats


def get_tgstat_channel_stats_requests(channel_url):
    html_content = fetch_tgstat_html(channel_url)
    tgstat_data = None
    if html_content:
        tgstat_data = parse_tgstat(html_content)
        logger.info(f"🔎 Итоговые данные: {tgstat_data}")
    return tgstat_data
