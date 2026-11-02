"""Products and Cart module: FR-06 to FR-10."""
import pytest

from pages.cart_page import CartPage
from pages.login_page import LoginPage
from utils.logger import step

BACKPACK = "Sauce Labs Backpack"
BIKE_LIGHT = "Sauce Labs Bike Light"


@pytest.mark.smoke
def test_fr06_products_visible(inventory):
    """FR-06: at least 6 products, each with a name, a price and an 'Add to cart' button."""
    products = inventory.products()
    step(f"Verify product cards ({len(products)} found)")
    assert len(products) >= 6
    for product in products:
        assert product["name"], "product without a name"
        assert product["price"].startswith("$"), f"bad price for {product['name']}"
        assert product["button"] == "Add to cart", f"{product['name']} button is {product['button']!r}"


@pytest.mark.smoke
def test_fr07_add_to_cart(inventory):
    """FR-07: adding an item raises the cart badge by 1 and the button changes to Remove."""
    before = inventory.cart_count()
    inventory.add_to_cart(BACKPACK)
    step("Verify the badge and the button")
    assert inventory.cart_count() == before + 1
    assert inventory.button_text(BACKPACK) == "Remove"


@pytest.mark.regression
def test_fr08_remove_from_cart(inventory):
    """FR-08: removing an added item lowers the badge and the button returns to 'Add to cart'."""
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)
    assert inventory.cart_count() == 2
    inventory.remove_from_cart(BACKPACK)
    step("Verify the badge and the button after removing")
    assert inventory.cart_count() == 1
    assert inventory.button_text(BACKPACK) == "Add to cart"


@pytest.mark.regression
def test_fr09_cart_details(inventory, driver):
    """FR-09: the cart lists the selected items with the same name and price as the Products page."""
    on_products = {p["name"]: p["price"] for p in inventory.products()}
    inventory.add_to_cart(BACKPACK)
    inventory.add_to_cart(BIKE_LIGHT)
    inventory.open_cart()
    in_cart = CartPage(driver).items()
    step(f"Verify cart contents: {in_cart}")
    assert sorted(i["name"] for i in in_cart) == sorted([BACKPACK, BIKE_LIGHT])
    for item in in_cart:
        assert item["price"] == on_products[item["name"]], f"price differs for {item['name']}"


@pytest.mark.regression
@pytest.mark.parametrize("path", ["inventory.html", "cart.html"])
def test_fr10_unauthorized_access_after_logout(inventory, driver, path):
    """FR-10: after logout, opening the inventory or cart page redirects to the Login page."""
    inventory.logout()
    login = LoginPage(driver)
    login.open_path(path)
    step("Verify the user is sent back to the Login page")
    assert login.is_displayed(), f"{path} opened without login"
    assert f"You can only access '/{path}' when you are logged in." in login.error_text()
