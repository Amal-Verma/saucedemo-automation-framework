"""Creates the Chrome WebDriver.

WebDriver Manager downloads a chromedriver that matches the installed Chrome. If it cannot
(for example no Chrome is installed, or the machine is offline), Selenium's own Selenium
Manager is used instead, which can also download Chrome for Testing.
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from config.config import PAGE_LOAD_TIMEOUT
from utils.logger import get_logger


def create_driver(headless: bool = False) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,900")
    options.add_argument("--disable-notifications")
    # Chrome's password manager shows a "change your password" pop-up on SauceDemo's
    # well-known demo password, which would cover the page; turn it off.
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
    })
    log = get_logger()
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        log.info("SETUP | Chrome started with WebDriver Manager")
    except Exception as error:  # noqa: BLE001 - fall back to Selenium Manager on any setup failure
        log.info("SETUP | WebDriver Manager unavailable (%s); using Selenium Manager",
                 str(error).splitlines()[0][:120])
        driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver
