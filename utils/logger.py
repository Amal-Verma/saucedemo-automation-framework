"""File logger: every line records the test name, the step and its status.

Format:  2026-11-01 21:30:05 | INFO | test_login_success | STEP | Enter username
The current test name is set by conftest.py before each test runs.
"""
import logging
from contextvars import ContextVar

from config.config import LOG_DIR, LOG_FILE

current_test: ContextVar[str] = ContextVar("current_test", default="-")


class _TestNameFilter(logging.Filter):
    def filter(self, record):
        record.test = current_test.get()
        return True


def get_logger(name: str = "saucedemo") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-5s | %(test)s | %(message)s", "%Y-%m-%d %H:%M:%S"))
    handler.addFilter(_TestNameFilter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def step(message: str) -> None:
    """Log one test step."""
    get_logger().info("STEP | %s", message)


def status(result: str, detail: str = "") -> None:
    """Log the final status of a test (PASSED, FAILED, SKIPPED, XFAIL)."""
    level = logging.ERROR if result == "FAILED" else logging.INFO
    get_logger().log(level, "STATUS | %s%s", result, f" | {detail}" if detail else "")
