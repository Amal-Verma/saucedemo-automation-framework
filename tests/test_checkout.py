"""Checkout module: FR-11 to FR-16."""
import pytest

from pages.cart_page import CartPage
from pages.checkout_complete_page import CheckoutCompletePage
from pages.checkout_info_page import CheckoutInfoPage
from pages.checkout_overview_page import CheckoutOverviewPage
from utils.data_loader import load_csv
from utils.logger import step

POSTAL_CODES = load_csv("postal_codes.csv")


@pytest.fixture
def checkout_info(inventory, driver):
    """Logged in, one item in the cart, on 'Checkout: Your Information'."""
    inventory.add_to_cart("Sauce Labs Backpack")
    inventory.open_cart()
    CartPage(driver).checkout()
    return CheckoutInfoPage(driver)


@pytest.mark.smoke
def test_fr11_navigate_to_checkout(checkout_info):
    """FR-11: Checkout on the Cart page opens 'Checkout: Your Information'."""
    step("Verify the Checkout: Your Information page")
    assert checkout_info.is_loaded()


@pytest.mark.regression
def test_fr12_first_name_mandatory(checkout_info):
    """FR-12: blank First Name shows an error and the user stays on the page."""
    checkout_info.fill("", "Verma", "40001")
    result = checkout_info.submit_and_get_result()
    step(f"Verify error: {result!r}")
    assert result == "Error: First Name is required"
    assert checkout_info.is_loaded()


@pytest.mark.regression
def test_fr13_last_name_mandatory(checkout_info):
    """FR-13: blank Last Name shows an error and the user stays on the page."""
    checkout_info.fill("Amal", "", "40001")
    result = checkout_info.submit_and_get_result()
    step(f"Verify error: {result!r}")
    assert result == "Error: Last Name is required"
    assert checkout_info.is_loaded()


def _postal_params():
    params = []
    for row in POSTAL_CODES:
        marks = []
        if row["known_defect"]:
            marks.append(pytest.mark.xfail(
                reason=f"{row['known_defect']}: SauceDemo accepts any non-empty postal code "
                       f"(see docs/TestCases.md)", strict=True))
        params.append(pytest.param(row, id=row["id"], marks=marks))
    return params


@pytest.mark.regression
@pytest.mark.parametrize("row", _postal_params())
def test_fr14_postal_code_boundary(checkout_info, row):
    """FR-14 (data-driven, BVA + EP): 5 and 6 digits are valid; 4 digits and non-numeric are invalid."""
    checkout_info.fill("Amal", "Verma", row["postal_code"])
    result = checkout_info.submit_and_get_result()
    step(f"Postal code {row['postal_code']!r} ({row['partition']}) gave: {result!r}")
    if row["expected"] == "valid":
        assert result == "overview", f"valid postal code rejected: {result!r}"
    else:
        assert result != "overview", "invalid postal code was accepted"
        assert result.startswith("Error:"), "no error message shown"


@pytest.mark.smoke
def test_fr15_checkout_overview(checkout_info, driver):
    """FR-15: valid First Name, Last Name and Postal Code lead to 'Checkout: Overview'."""
    checkout_info.fill("Amal", "Verma", "40001")
    checkout_info.click_continue()
    step("Verify the Overview page")
    assert CheckoutOverviewPage(driver).is_loaded()


@pytest.mark.smoke
def test_fr16_finish_order(checkout_info, driver):
    """FR-16: Finish on the Overview page shows the order success message."""
    checkout_info.fill("Amal", "Verma", "40001")
    checkout_info.click_continue()
    overview = CheckoutOverviewPage(driver)
    assert overview.is_loaded()
    overview.finish()
    complete = CheckoutCompletePage(driver)
    step("Verify the success message")
    assert complete.is_loaded()
    assert complete.success_message() == "Thank you for your order!"
