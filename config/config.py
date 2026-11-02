"""Central settings for the SauceDemo framework. Values can be overridden with environment variables."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com/")
USERNAME = os.getenv("SAUCE_USERNAME", "standard_user")
PASSWORD = os.getenv("SAUCE_PASSWORD", "secret_sauce")

# Seconds an explicit wait polls before failing.
EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", "10"))
# Seconds to give the browser to load a page.
PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))

TESTDATA_DIR = ROOT / "testdata"
REPORTS_DIR = ROOT / "reports"
SCREENSHOT_DIR = REPORTS_DIR / "screenshots"
LOG_DIR = REPORTS_DIR / "logs"
LOG_FILE = LOG_DIR / "test_run.log"
