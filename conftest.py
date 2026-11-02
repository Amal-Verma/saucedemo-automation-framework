"""Shared fixtures and hooks: browser per test, logged-in session, logging, screenshot on failure."""
import base64
import re
from datetime import datetime

import pytest

from config.config import PASSWORD, SCREENSHOT_DIR, USERNAME
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.driver_factory import create_driver
from utils.logger import current_test, get_logger, status


def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", help="run Chrome without a window")


@pytest.fixture
def driver(request):
    """A fresh Chrome for every test, so tests never depend on each other."""
    browser = create_driver(headless=request.config.getoption("--headless"))
    yield browser
    browser.quit()


@pytest.fixture
def login_page(driver):
    return LoginPage(driver).open()


@pytest.fixture
def inventory(login_page, driver):
    """Logged in as the standard user, on the Products page."""
    login_page.login_as_valid_user(USERNAME, PASSWORD)
    return InventoryPage(driver)


@pytest.fixture(autouse=True)
def _log_test(request):
    token = current_test.set(request.node.name)
    get_logger().info("START | %s", request.node.nodeid)
    yield
    current_test.reset(token)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" and not report.failed:
        return
    token = current_test.set(item.name)
    try:
        expected_failure = hasattr(report, "wasxfail")
        if report.failed or expected_failure:
            driver = item.funcargs.get("driver")
            if driver is not None:
                _save_screenshot(item, report, driver)
        if report.when == "call" or report.failed:
            if expected_failure:
                status("XFAIL" if report.skipped else "XPASS", report.wasxfail)
            elif report.failed:
                crash = getattr(report.longrepr, "reprcrash", None)
                message = (crash.message if crash else str(report.longrepr)).splitlines()[0][:200]
                status("FAILED", f"{report.when}: {message}")
            else:
                status("PASSED")
    finally:
        current_test.reset(token)


def _save_screenshot(item, report, driver):
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.name)[:80]
    path = SCREENSHOT_DIR / f"{safe}_{datetime.now():%Y%m%d_%H%M%S}.png"
    try:
        png_base64 = driver.get_screenshot_as_base64()
    except Exception:  # noqa: BLE001 - the browser may already be gone
        return
    path.write_bytes(base64.b64decode(png_base64))
    get_logger().info("EVIDENCE | screenshot saved: %s", path.relative_to(SCREENSHOT_DIR.parent.parent))
    html = item.config.pluginmanager.getplugin("html")
    if html is not None:
        extras = getattr(report, "extras", [])
        extras.append(html.extras.png(png_base64, name=path.name))
        report.extras = extras
