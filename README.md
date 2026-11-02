# SauceDemo Automation Framework

Selenium 4 + PyTest automation framework and JMeter performance test for
[SauceDemo](https://www.saucedemo.com/) (Software Testing Lab case study).

- Page Object Model, explicit waits only (no `time.sleep`)
- Smoke and regression markers for selective runs
- Data-driven tests from JSON and CSV
- Screenshot on failure, step-by-step log file, self-contained HTML report
- JMeter test plan for 20 users with an NFR pass/fail summary

## Project structure

```
saucedemo-framework/
├── config/config.py            URL, credentials, timeouts, report paths (env overrides)
├── pages/                      Page Object Model: locators + actions per page
│   ├── base_page.py            explicit-wait helpers shared by all pages
│   ├── login_page.py
│   ├── inventory_page.py       Products page, cart badge, side menu / logout
│   ├── cart_page.py
│   ├── checkout_info_page.py   Checkout: Your Information
│   ├── checkout_overview_page.py
│   └── checkout_complete_page.py
├── tests/                      test_login.py, test_products_cart.py, test_checkout.py
├── testdata/                   login_negative.json, username_boundary.json, postal_codes.csv
├── utils/                      driver_factory.py, logger.py, data_loader.py
├── conftest.py                 fixtures, screenshot-on-failure hook, test logging
├── pytest.ini                  markers, HTML report options
├── docs/TestCases.md           EP/BVA test design, test cases, traceability, defects
├── reports/                    report.html, screenshots/, logs/ (created by a run)
└── performance/
    ├── jmx/saucedemo_weekend_lab.jmx
    ├── results/results.jtl, aggregate.csv
    ├── html_report/            JMeter HTML dashboard
    ├── scripts/aggregate.py    builds aggregate.csv and checks the NFRs
    └── Findings.md             NFR pass/fail with P95 and error %
```

## Setup (Windows 10/11)

Prerequisites: Google Chrome, Python 3.11 or newer, and for performance testing Java 8+ with
Apache JMeter 5.6+.

```powershell
cd saucedemo-framework
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

(Linux/macOS: `python3 -m venv .venv` and `source .venv/bin/activate`.)

The Chrome driver is set up automatically: WebDriver Manager downloads a chromedriver that
matches the installed Chrome. If that is not possible, Selenium Manager (built into Selenium 4)
is used instead.

## Running the tests

| What | Command |
|---|---|
| Smoke suite (6 core flows) | `pytest -m smoke` |
| Regression suite (negative and boundary cases) | `pytest -m regression` |
| Full suite (23 test cases) | `pytest` |
| Without a browser window | add `--headless`, e.g. `pytest -m smoke --headless` |
| One requirement | `pytest -k fr14` |
| Show known defects as failures | `pytest --runxfail` |

After a run:
- **HTML report:** `reports/report.html` (self-contained; failure screenshots are embedded)
- **Screenshots on failure:** `reports/screenshots/<test>_<timestamp>.png`
- **Log:** `reports/logs/test_run.log`, one line per step: `time | level | test name | STEP / STATUS | detail`

Expected result of the full suite: **21 passed, 2 xfailed**. The two expected failures are
TC-14a and TC-14d: SauceDemo accepts a 4-digit or non-numeric postal code, which FR-14 says must
be rejected (defect DEF-01 in `docs/TestCases.md`). They are marked `xfail(strict=True)`, so the
defect is recorded with a screenshot without breaking the build.

## Framework design

- **Page Object Model:** each page class in `pages/` holds its locators and the actions a user
  can take there; tests only call page methods and assert results.
- **Explicit waits:** `BasePage` waits for elements to be visible or clickable with
  `WebDriverWait`. There are no fixed sleeps anywhere. Two SauceDemo quirks are handled with
  waits, not sleeps:
  - Selenium's `clear()` does not reset React's input state, so `BasePage.type()` clears with
    Ctrl+A and Delete, then waits until the field really holds the typed value.
  - A click that lands while React is still rendering can be ignored, so `click_until()` clicks,
    waits for the expected result (for example the next URL) and clicks again if needed.
- **Data-driven tests:** `test_fr02_to_fr04_login_failure` (JSON), `test_fr05_username_length_boundary`
  (JSON) and `test_fr14_postal_code_boundary` (CSV) take their cases from `testdata/`.
- **Markers:** `smoke` for core happy-path flows, `regression` for negative and boundary cases.
- **Isolation:** every test gets a fresh browser, so tests can run in any order.
- **Configuration:** URL, credentials and timeouts are in `config/config.py` and can be overridden
  with environment variables (`BASE_URL`, `SAUCE_USERNAME`, `SAUCE_PASSWORD`, `EXPLICIT_WAIT`).

## Requirement coverage

All 16 functional requirements are automated (the 6 mandatory ones plus all 10 others, including
negative and boundary cases). See `docs/TestCases.md` for the test design and the traceability matrix.

| Module | Requirements | Test file |
|---|---|---|
| Login | FR-01 to FR-05 | `tests/test_login.py` |
| Products and Cart | FR-06 to FR-10 | `tests/test_products_cart.py` |
| Checkout | FR-11 to FR-16 | `tests/test_checkout.py` |

## Performance test (JMeter)

Load profile: 20 users, 60 s ramp-up, 3 minutes, random think time 0 to 500 ms.

```powershell
cd performance
jmeter -n -t jmx\saucedemo_weekend_lab.jmx -Jjmeter.save.saveservice.subresults=false ^
       -l results\results.jtl -e -o html_report
python scripts\aggregate.py
```

- `results.jtl` and `html_report/` must not exist before the run (JMeter refuses to overwrite them).
- `-Jjmeter.save.saveservice.subresults=false` stores one sample per page load ("Login page",
  "Products page"), so the P95 values are per page.
- `aggregate.py` writes `results/aggregate.csv` (the same columns as JMeter's Aggregate Report)
  and prints the NFR pass/fail check.
- The load profile can be changed without editing the plan: `-Jusers=20 -Jrampup=60 -Jduration=180`.
- To open the plan in the GUI: `jmeter -t jmx\saucedemo_weekend_lab.jmx`.

Results and the NFR verdicts are in `performance/Findings.md`.

## Demo script

1. `pytest -m smoke` (with the browser visible): login, products, add to cart, checkout, finish.
2. `pytest -m regression`: negative and boundary cases, including the data-driven ones.
3. Open `reports/report.html`: results, durations, and the screenshots of TC-14a and TC-14d.
4. Show `reports/logs/test_run.log` and `reports/screenshots/`.
5. Show `docs/TestCases.md` (EP/BVA design and traceability) and `performance/Findings.md`.
