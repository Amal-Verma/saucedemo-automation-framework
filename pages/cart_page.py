from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.logger import step


class CartPage(BasePage):
    CART_ITEM = (By.CSS_SELECTOR, '[data-test="inventory-item"]')
    ITEM_NAME = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')
    ITEM_PRICE = (By.CSS_SELECTOR, '[data-test="inventory-item-price"]')
    CHECKOUT = (By.ID, "checkout")

    def items(self) -> list[dict]:
        rows = self.find_all(self.CART_ITEM)
        return [{"name": r.find_element(*self.ITEM_NAME).text,
                 "price": r.find_element(*self.ITEM_PRICE).text} for r in rows]

    def checkout(self):
        step("Click Checkout")
        self.click_until(self.CHECKOUT, EC.url_contains("checkout-step-one.html"))
