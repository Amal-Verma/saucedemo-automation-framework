from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class CheckoutCompletePage(BasePage):
    HEADER = (By.CSS_SELECTOR, '[data-test="complete-header"]')

    def is_loaded(self) -> bool:
        return self.wait_for_url("checkout-complete.html") and self.title() == "Checkout: Complete!"

    def success_message(self) -> str:
        return self.text_of(self.HEADER)
