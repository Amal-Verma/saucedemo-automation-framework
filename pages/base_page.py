"""Base page: shared explicit-wait helpers used by every page object. No fixed sleeps."""
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import BASE_URL, EXPLICIT_WAIT
from utils.logger import step


class BasePage:
    TITLE = (By.CSS_SELECTOR, '[data-test="title"]')
    ERROR = (By.CSS_SELECTOR, '[data-test="error"]')

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.wait = WebDriverWait(driver, EXPLICIT_WAIT)

    # ---------- navigation ----------
    def open_path(self, path: str = ""):
        step(f"Open {BASE_URL}{path}")
        self.driver.get(BASE_URL + path)

    def wait_for_url(self, fragment: str, timeout: int = EXPLICIT_WAIT) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.url_contains(fragment))
            return True
        except TimeoutException:
            return False

    @property
    def url(self) -> str:
        return self.driver.current_url

    # ---------- finding ----------
    def find(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator):
        self.wait.until(EC.presence_of_all_elements_located(locator))
        return self.driver.find_elements(*locator)

    def is_visible(self, locator, timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except TimeoutException:
            return False

    def text_of(self, locator) -> str:
        return self.find(locator).text

    # ---------- actions ----------
    def click(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def click_until(self, locator, condition, attempts: int = 3):
        """Click, then wait for `condition`; click again if the page did not react.

        SauceDemo is a React app: a click that lands while the page is still rendering can be
        ignored. Retrying with an explicit wait keeps the test stable without fixed sleeps.
        """
        for attempt in range(1, attempts + 1):
            self.click(locator)
            try:
                WebDriverWait(self.driver, 4).until(condition)
                return
            except TimeoutException:
                if attempt == attempts:
                    raise

    def type(self, locator, text: str):
        """Clear the field and type `text`, then wait until the field really holds it.

        Selenium's clear() does not reset React's state on SauceDemo, so the field is cleared
        with Ctrl+A and Delete. If the app re-renders and drops the typed text, it is retyped.
        """
        for _ in range(3):
            field = self.find(locator)
            field.send_keys(Keys.CONTROL, "a")
            field.send_keys(Keys.DELETE)
            if text:
                field.send_keys(text)
            try:
                WebDriverWait(self.driver, 2).until(
                    lambda d: d.find_element(*locator).get_attribute("value") == text)
                return
            except TimeoutException:
                continue
        raise AssertionError(f"Field {locator} did not keep the value {text!r}")

    # ---------- common elements ----------
    def title(self) -> str:
        return self.text_of(self.TITLE)

    def error_text(self) -> str:
        return self.text_of(self.ERROR) if self.is_visible(self.ERROR) else ""
