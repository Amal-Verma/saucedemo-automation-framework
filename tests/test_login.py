"""Login module: FR-01 to FR-05."""
import pytest

from config.config import PASSWORD, USERNAME
from pages.inventory_page import InventoryPage
from utils.data_loader import load_json
from utils.logger import step

NEGATIVE_LOGINS = load_json("login_negative.json")
USERNAME_BOUNDARY = load_json("username_boundary.json")


@pytest.mark.smoke
def test_fr01_login_success(login_page, driver):
    """FR-01: valid credentials open the Products page with the title 'Products'."""
    login_page.login_as_valid_user(USERNAME, PASSWORD)
    step("Verify the Products page is shown")
    assert InventoryPage(driver).is_loaded(), f"Products page not shown, URL is {driver.current_url}"


@pytest.mark.regression
@pytest.mark.parametrize("data", NEGATIVE_LOGINS, ids=[d["id"] for d in NEGATIVE_LOGINS])
def test_fr02_to_fr04_login_failure(login_page, data):
    """FR-02, FR-03, FR-04 (data-driven): invalid or blank credentials show an error banner
    and the user stays on the Login page."""
    login_page.login(data["username"], data["password"])
    step(f"Verify error for: {data['case']}")
    assert login_page.error_text() == data["error"]
    assert login_page.is_displayed(), "user left the Login page"
    assert "inventory" not in login_page.url


@pytest.mark.regression
@pytest.mark.parametrize("data", USERNAME_BOUNDARY, ids=[d["id"] for d in USERNAME_BOUNDARY])
def test_fr05_username_length_boundary(login_page, data):
    """FR-05 (data-driven, boundary value analysis): usernames of 30, 31 and 50 characters
    cannot log in; the field keeps the full text and an error banner is shown."""
    username = "u" * data["length"]
    login_page.login(username, PASSWORD)
    step(f"Verify login fails for a {data['partition']} username")
    assert login_page.username_value() == username, "the username field cut the text"
    assert login_page.error_text().startswith("Epic sadface:"), "no error banner shown"
    assert login_page.is_displayed()
