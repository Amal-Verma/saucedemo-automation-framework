from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.logger import step


class CheckoutOverviewPage(BasePage):
    FINISH = (By.ID, "finish")

    def is_loaded(self) -> bool:
        return self.wait_for_url("checkout-step-two.html") and self.title() == "Checkout: Overview"

    def finish(self):
        step("Click Finish")
        self.click_until(self.FINISH, EC.url_contains("checkout-complete.html"))
