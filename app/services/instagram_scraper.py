import time
from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.utils.driver import create_firefox_driver
from app.utils.config import Settings

settings = Settings()


def login_to_instagram(driver):
    """Логинится в Instagram через Selenium."""
    logger.info("Авторизация в Instagram...")
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    # Вводим логин
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
    username_input.send_keys(settings.INSTAGRAM_USERNAME)

    # Вводим пароль
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(settings.INSTAGRAM_PASSWORD)
    password_input.send_keys(Keys.RETURN)

    # Ждём загрузку страницы после входа
    time.sleep(5)

    # Проверяем, залогинились ли мы
    if "accounts/onetap" in driver.current_url:
        logger.info("Instagram предлагает сохранить вход (пропускаем)")
        driver.find_element(By.XPATH, "//button[text()='Не сейчас']").click()
        time.sleep(2)

    logger.info("Авторизация успешна!")


def get_instagram_comments(post_url, max_comments=20):
    """Парсит комментарии с поста Instagram."""
    driver = create_firefox_driver()
    try:
        login_to_instagram(driver)

        logger.info(f"Открываем пост {post_url}")
        driver.get(post_url)
        time.sleep(5)

        comments = set()
        last_height = driver.execute_script(
            "return document.documentElement.scrollHeight")

        logger.info("Начинаем прокрутку комментариев...")

        while len(comments) < max_comments:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "ul.XQXOT > div"))
                )
            except Exception as e:
                logger.warning(
                    f"Комментарии не подгружаются! Error message: {e}")

            comment_elements = driver.find_elements(
                By.CSS_SELECTOR, "span._aacl._aaco._aacu._aacx._aad7._aade")

            if not comment_elements:
                logger.warning(
                    "Комментарии не найдены! Возможно, пост закрыт.")
                break

            for comment in comment_elements:
                text = comment.text.strip()
                if text and text not in comments:
                    comments.add(text)
                    logger.debug(f"Добавлен комментарий: {text[:50]}...")

                if len(comments) >= max_comments:
                    logger.info(
                        "Достигнуто максимальное количество комментариев.")
                    break

            new_height = driver.execute_script(
                "return document.documentElement.scrollHeight")
            if new_height == last_height:
                logger.info(
                    "Достигнут конец страницы, больше комментариев нет.")
                break
            last_height = new_height

        if not comments:
            logger.warning("Не удалось собрать ни одного комментария!")

        return {"post_url": post_url, "comments": list(comments)}

    except Exception as e:
        logger.error(f"Ошибка при парсинге: {e}")
        return {"error": str(e)}

    finally:
        logger.info("Закрываем браузер...")
        driver.quit()
