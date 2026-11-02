from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.logger import step


class LoginPage(BasePage):
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    LOGO = (By.CLASS_NAME, "login_logo")

    def open(self):
        self.open_path("")
        self.find(self.USERNAME)
        return self

    def enter_username(self, username: str):
        step(f"Enter username ({len(username)} characters)")
        self.type(self.USERNAME, username)

    def enter_password(self, password: str):
        step("Enter password" if password else "Leave password blank")
        self.type(self.PASSWORD, password)

    def click_login(self):
        step("Click Login")
        self.click(self.LOGIN_BUTTON)

    def login(self, username: str, password: str):
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def login_as_valid_user(self, username: str, password: str):
        """Log in and wait for the Products page (retries the click if it was ignored)."""
        self.enter_username(username)
        self.enter_password(password)
        step("Click Login and wait for the Products page")
        self.click_until(self.LOGIN_BUTTON, EC.url_contains("inventory.html"))

    def is_displayed(self) -> bool:
        return self.is_visible(self.LOGIN_BUTTON) and self.is_visible(self.USERNAME)

    def username_value(self) -> str:
        return self.find(self.USERNAME).get_attribute("value")
