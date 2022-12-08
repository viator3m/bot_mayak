import os

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By

from logger import logger


def driver_init():
    """Создание и настройка экземпляра браузера."""
    service = Service(
        executable_path=PATH_TO_DRIVER)
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument("--window-size=1920,1080")
    user_agent = ('Mozilla/5.0 (X11; Linux x86_64)'
                  ' AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/60.0.3112.50 Safari/537.36')
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)
    return driver


def get_price(url, xpath):
    """Получение цены со страницы товара."""
    brow.get(url)
    try:
        price = brow.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        logger.error(f'Не удалось найти элемент на {url}')
        return '_'
    text_price = price.text.split('₽')[0]
    price = ''.join([i for i in text_price if i.isdigit()])
    return price


def get_average(data: list[list[str]]) -> list[int]:
    """Получение средней цены товара."""
    prices = []
    amount = 0

    for items in data:
        _, name, url, xpath = items
        price = get_price(url, xpath)
        try:
            prices.append(int(price))
        except ValueError:
            logger.error(f'Ошибка при парсинге {name}')
        else:
            amount += 1
            logger.info(f'{name} цена: {price}₽')

    return [sum(prices) // len(prices), amount]


def file_info(data: list[list]) -> str:
    """Возвращает строку с содержимым файла для ответа пользователю."""
    text = ''
    for row in data:
        _, name, url, xpath = row
        text += f"""
        name: {name[:25]}
        url: {url[:20]}...
        xpath: {xpath[:20]}...
        """
    return text


BASE_PATH = os.path.dirname(os.path.abspath(__file__))
PATH_TO_DRIVER = BASE_PATH + '/driver/chromedriver'
brow = driver_init()
