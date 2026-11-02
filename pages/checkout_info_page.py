from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from utils.logger import step


class CheckoutInfoPage(BasePage):
    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE = (By.ID, "continue")

    def is_loaded(self) -> bool:
        return self.wait_for_url("checkout-step-one.html") and self.title() == "Checkout: Your Information"

    def fill(self, first: str, last: str, postal: str):
        step(f"Fill form: first={first!r} last={last!r} postal={postal!r}")
        self.type(self.FIRST_NAME, first)
        self.type(self.LAST_NAME, last)
        self.type(self.POSTAL_CODE, postal)

    def click_continue(self):
        step("Click Continue")
        self.click(self.CONTINUE)

    def submit_and_get_result(self) -> str:
        """Click Continue and return 'overview' if the Overview page opened, else the error text."""
        self.click_continue()
        if self.wait_for_url("checkout-step-two.html", timeout=4):
            return "overview"
        return self.error_text()
