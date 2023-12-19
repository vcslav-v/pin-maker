from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from urllib.parse import unquote, urlparse
from time import sleep

from pin_maker.config import PINTEREST_LOGIN, PINTEREST_PASSWORD, logger, PIN_DESCRIPTION_COUNT, NESESSARY_DESC_COUNT
from pin_maker.browser import Browser
from pin_maker import db_tools
from pb_admin import schemas as pb_schemas


def make_description(tags: list[pb_schemas.Tag], description: str) -> str:
    """Make description for pin."""
    tags = sorted(tags, key=lambda x: x.no_index)
    _tags = []
    for tag in tags:
        _tags.append(f"#{'_'.join(tag.name.split(' ')).capitalize()}")
        if len(' '.join(_tags)) >= PIN_DESCRIPTION_COUNT - NESESSARY_DESC_COUNT:
            break
    tags = ' '.join(_tags)
    description = description[:PIN_DESCRIPTION_COUNT - len(tags) - 5]
    description = f'{description}... {tags}'
    return description


def _download_to_selenium(driver: webdriver, link: str) -> str:
    driver.execute_script(f'''
        var anchor = document.createElement("a");
        anchor.href = "{link}"
        document.body.appendChild(anchor);
        anchor.click();
        document.body.removeChild(anchor);
    ''')
    sleep(1)
    return f'/home/selenium/Downloads/{unquote(urlparse(link).path.split("/")[-1])}'


def _pinterest_login(driver: webdriver):
    login_button = WebDriverWait(driver, 20).until(
        lambda x: x.find_element(By.XPATH, '//div[contains(text(), "Log in")]/ancestor::button[1]')
    )
    login_button.click()
    login_input = driver.find_element(By.ID, 'email')
    password_input = driver.find_element(By.ID, 'password')
    login_input.send_keys(PINTEREST_LOGIN)
    password_input.send_keys(PINTEREST_PASSWORD)
    login_button = WebDriverWait(driver, 20).until(
        lambda x: x.find_element(By.XPATH, '//div[@data-test-id="login-modal-default"]//div[contains(text(), "Log in")]/ancestor::button[1]')
    )
    login_button.click()
    return _is_logged_in(driver)


def _send_csv_bulk(driver: webdriver, csv_path: str):
    driver.get('https://www.pinterest.com/settings/bulk-create-pins')
    file_input = WebDriverWait(driver, 20).until(
        lambda x: x.find_element(By.ID, 'csv-input')
    )
    file_input.send_keys(csv_path)
    try:
        driver.WebDriverWait(driver, 20).until(
            lambda x: x.find_element(By.XPATH, '//h1[contains(text(),"Upload successful")]')
        )
        logger.info('Upload successful')
    except TimeoutException:
        logger.error('Upload failed')
        exit(1)


def _is_logged_in(driver: webdriver):
    driver.get('https://www.pinterest.com/')
    try:
        WebDriverWait(driver, 20).until(
            lambda x: x.find_element(By.XPATH, '//div[contains(text(), "Log in")]/ancestor::button[1]')
        )
        return False
    except TimeoutException:
        return True


def _log_in_pinterest(driver: webdriver, cookies: list):
    driver.get('https://www.pinterest.com/')
    for cookie in cookies:
        driver.add_cookie(cookie)
    if not _is_logged_in(driver):
        try:
            is_logged = _pinterest_login(driver)
        except:
            logger.error('Login failed')
            driver.quit()
            exit(1)
        if not is_logged:
            logger.error('Login failed')
            driver.quit()
            exit(1)


def upload_csv(link_to_csv: str):
    with Browser() as browser:
        driver = browser.driver
        csv_path = _download_to_selenium(driver, link_to_csv)
        cookies = db_tools.get_cookies()
        _log_in_pinterest(driver, cookies)
        _send_csv_bulk(driver, csv_path)
        db_tools.update_cookies(driver.get_cookies())
