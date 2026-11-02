from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage
from utils.logger import step


class InventoryPage(BasePage):
    ITEM = (By.CSS_SELECTOR, '[data-test="inventory-item"]')
    ITEM_NAME = (By.CSS_SELECTOR, '[data-test="inventory-item-name"]')
    ITEM_PRICE = (By.CSS_SELECTOR, '[data-test="inventory-item-price"]')
    ITEM_BUTTON = (By.CSS_SELECTOR, "button")
    CART_BADGE = (By.CSS_SELECTOR, '[data-test="shopping-cart-badge"]')
    CART_LINK = (By.CSS_SELECTOR, '[data-test="shopping-cart-link"]')
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")

    @staticmethod
    def _button_for(product: str):
        return (By.XPATH, f'//div[@data-test="inventory-item"][.//div[@data-test="inventory-item-name"'
                          f' and normalize-space()="{product}"]]//button')

    def is_loaded(self) -> bool:
        return self.wait_for_url("inventory.html") and self.title() == "Products"

    def products(self) -> list[dict]:
        """Name, price and button text of every product card on the page."""
        cards = self.find_all(self.ITEM)
        return [{
            "name": card.find_element(*self.ITEM_NAME).text,
            "price": card.find_element(*self.ITEM_PRICE).text,
            "button": card.find_element(*self.ITEM_BUTTON).text,
        } for card in cards]

    def button_text(self, product: str) -> str:
        return self.find(self._button_for(product)).text

    def add_to_cart(self, product: str):
        step(f"Add '{product}' to the cart")
        self.click_until(self._button_for(product),
                         EC.text_to_be_present_in_element(self._button_for(product), "Remove"))

    def remove_from_cart(self, product: str):
        step(f"Remove '{product}' from the cart")
        self.click_until(self._button_for(product),
                         EC.text_to_be_present_in_element(self._button_for(product), "Add to cart"))

    def cart_count(self) -> int:
        """Number on the cart badge; 0 when the badge is not shown."""
        badges = self.driver.find_elements(*self.CART_BADGE)
        return int(badges[0].text) if badges else 0

    def open_cart(self):
        step("Open the cart")
        self.click_until(self.CART_LINK, EC.url_contains("cart.html"))

    def logout(self):
        step("Log out through the side menu")
        self.click(self.MENU_BUTTON)
        self.click_until(self.LOGOUT_LINK, EC.visibility_of_element_located((By.ID, "login-button")))
