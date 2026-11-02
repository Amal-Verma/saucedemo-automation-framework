# Test Cases, Test Design and Traceability

Application under test: https://www.saucedemo.com/ (user `standard_user`, password `secret_sauce`).
Each requirement (FR) from the case study is turned into test cases using **Equivalence
Partitioning (EP)** and **Boundary Value Analysis (BVA)**. Every FR is automated.

## 1. Test design by requirement

### Login module

| FR | Technique | Partitions / boundaries | Test cases |
|---|---|---|---|
| FR-01 Login success | EP (valid partition) | valid username + valid password | TC-01 |
| FR-02 Invalid password | EP (invalid partition) | valid username + wrong password; same password in wrong letter case | TC-02a, TC-02b |
| FR-03 Blank username | EP (empty partition) | username empty, password valid | TC-03 |
| FR-04 Blank password | EP (empty partition) | username valid, password empty | TC-04 |
| FR-05 Username length | BVA | valid lengths 1 to 30, invalid lengths over 30. Boundary values: **30** (on the boundary), **31** (just above), **50** (well above) | TC-05a, TC-05b, TC-05c |

Note on FR-05: a 30-character username is in the valid *length* partition, but no registered user
has a 30-character name, so it must still fail with an error banner (EP: valid length, invalid
account). The test also checks that the field keeps the full text (no silent cut-off).

### Products and cart module

| FR | Technique | Test cases |
|---|---|---|
| FR-06 Products visible | EP: at least 6 items, each with name, price and "Add to cart" | TC-06 |
| FR-07 Add to cart | State transition: badge 0 to 1, button "Add to cart" to "Remove" | TC-07 |
| FR-08 Remove from cart | State transition: badge 2 to 1, button "Remove" to "Add to cart" | TC-08 |
| FR-09 Cart details | Comparison: names and prices in the cart equal those on the Products page | TC-09 |
| FR-10 Unauthorized access | EP: protected pages after logout (inventory, cart) | TC-10a, TC-10b |

### Checkout module

| FR | Technique | Partitions / boundaries | Test cases |
|---|---|---|---|
| FR-11 Navigate to checkout | EP (valid flow) | Cart to Checkout: Your Information | TC-11 |
| FR-12 First name mandatory | EP (empty partition) | first name empty, others valid | TC-12 |
| FR-13 Last name mandatory | EP (empty partition) | last name empty, others valid | TC-13 |
| FR-14 Postal code | BVA + EP | numeric length below 5 invalid, 5 to 6 valid; non-numeric invalid. Values: **4 digits** (below the lower boundary), **5 digits** (lower boundary), **6 digits** (upper boundary), **"12a45"** (non-numeric partition) | TC-14a to TC-14d |
| FR-15 Checkout overview | EP (valid partition) | all three fields valid | TC-15 |
| FR-16 Finish order | EP (valid flow) | Overview then Finish | TC-16 |

## 2. Test case list

| TC ID | FR | Type | Input / data | Expected result | Automated test | Marker |
|---|---|---|---|---|---|---|
| TC-01 | FR-01 | Positive | standard_user / secret_sauce | Products page, title "Products" | `test_fr01_login_success` | smoke |
| TC-02a | FR-02 | Negative | standard_user / wrong_password | "Epic sadface: Username and password do not match any user in this service", stays on Login | `test_fr02_to_fr04_login_failure[TC-02a]` | regression |
| TC-02b | FR-02 | Negative | standard_user / SECRET_SAUCE | same error, stays on Login | `test_fr02_to_fr04_login_failure[TC-02b]` | regression |
| TC-03 | FR-03 | Negative | blank / secret_sauce | "Epic sadface: Username is required" | `test_fr02_to_fr04_login_failure[TC-03]` | regression |
| TC-04 | FR-04 | Negative | standard_user / blank | "Epic sadface: Password is required" | `test_fr02_to_fr04_login_failure[TC-04]` | regression |
| TC-05a | FR-05 | Boundary | username of 30 characters | login fails, error banner, field keeps 30 characters | `test_fr05_username_length_boundary[TC-05a]` | regression |
| TC-05b | FR-05 | Boundary | username of 31 characters | login fails, error banner | `test_fr05_username_length_boundary[TC-05b]` | regression |
| TC-05c | FR-05 | Boundary | username of 50 characters | login fails, error banner | `test_fr05_username_length_boundary[TC-05c]` | regression |
| TC-06 | FR-06 | Positive | logged in | 6 or more items, each with name, price, "Add to cart" | `test_fr06_products_visible` | smoke |
| TC-07 | FR-07 | Positive | add Sauce Labs Backpack | badge +1, button "Remove" | `test_fr07_add_to_cart` | smoke |
| TC-08 | FR-08 | Positive | add Backpack and Bike Light, remove Backpack | badge 2 to 1, button "Add to cart" | `test_fr08_remove_from_cart` | regression |
| TC-09 | FR-09 | Positive | add Backpack and Bike Light, open cart | both items listed with the same prices | `test_fr09_cart_details` | regression |
| TC-10a | FR-10 | Negative | logout, open /inventory.html | Login page, "You can only access '/inventory.html' when you are logged in." | `test_fr10_unauthorized_access_after_logout[inventory.html]` | regression |
| TC-10b | FR-10 | Negative | logout, open /cart.html | Login page, same message for '/cart.html' | `test_fr10_unauthorized_access_after_logout[cart.html]` | regression |
| TC-11 | FR-11 | Positive | Cart, click Checkout | "Checkout: Your Information" | `test_fr11_navigate_to_checkout` | smoke |
| TC-12 | FR-12 | Negative | first name blank | "Error: First Name is required", stays on page | `test_fr12_first_name_mandatory` | regression |
| TC-13 | FR-13 | Negative | last name blank | "Error: Last Name is required", stays on page | `test_fr13_last_name_mandatory` | regression |
| TC-14a | FR-14 | Boundary | postal 1234 | error, stays on page | `test_fr14_postal_code_boundary[TC-14a]` | regression |
| TC-14b | FR-14 | Boundary | postal 12345 | Overview page | `test_fr14_postal_code_boundary[TC-14b]` | regression |
| TC-14c | FR-14 | Boundary | postal 123456 | Overview page | `test_fr14_postal_code_boundary[TC-14c]` | regression |
| TC-14d | FR-14 | Negative | postal 12a45 | error, stays on page | `test_fr14_postal_code_boundary[TC-14d]` | regression |
| TC-15 | FR-15 | Positive | Amal / Verma / 40001 | "Checkout: Overview" | `test_fr15_checkout_overview` | smoke |
| TC-16 | FR-16 | Positive | Overview, click Finish | "Thank you for your order!" | `test_fr16_finish_order` | smoke |

Data-driven tests read their inputs from `testdata/`:
`login_negative.json` (TC-02a to TC-04), `username_boundary.json` (TC-05a to TC-05c) and
`postal_codes.csv` (TC-14a to TC-14d).

## 3. Traceability matrix and latest result

Latest full run: 23 test cases, 21 passed, 2 expected failures (known defect DEF-01).

| Requirement | Mandatory | Test cases | Result |
|---|---|---|---|
| FR-01 | yes | TC-01 | Pass |
| FR-02 | yes | TC-02a, TC-02b | Pass |
| FR-03 | | TC-03 | Pass |
| FR-04 | | TC-04 | Pass |
| FR-05 | | TC-05a, TC-05b, TC-05c | Pass |
| FR-06 | | TC-06 | Pass |
| FR-07 | yes | TC-07 | Pass |
| FR-08 | | TC-08 | Pass |
| FR-09 | | TC-09 | Pass |
| FR-10 | | TC-10a, TC-10b | Pass |
| FR-11 | | TC-11 | Pass |
| FR-12 | yes | TC-12 | Pass |
| FR-13 | | TC-13 | Pass |
| FR-14 | yes | TC-14a to TC-14d | **Fail** for TC-14a and TC-14d (DEF-01); TC-14b and TC-14c pass |
| FR-15 | | TC-15 | Pass |
| FR-16 | yes | TC-16 | Pass |

## 4. Defects found

| ID | Requirement | Severity | Description | Steps | Expected | Actual | Evidence |
|---|---|---|---|---|---|---|---|
| DEF-01 | FR-14 | Medium | Postal Code has no numeric or length validation | Log in, add an item, Cart, Checkout, enter Amal / Verma / `1234` (or `12a45`), Continue | Error message, user stays on "Checkout: Your Information" | "Checkout: Overview" opens; any non-empty postal code is accepted | Screenshots in `reports/screenshots/test_fr14_postal_code_boundary_TC-14a_*.png` and `..._TC-14d_*.png`; HTML report |

TC-14a and TC-14d are marked `xfail(strict=True)` with the defect ID, so the suite stays green while
the defect is open but still records it, with a screenshot, in the report and the log. When the
defect is fixed, the tests pass unexpectedly and `strict=True` turns that into a failure, so the marker
gets removed. Run `pytest --runxfail` to see them as plain failures.

Observation on FR-05 (not a defect): the username field has no 30-character limit and accepts
50 characters, but the login still fails with the error banner, so FR-05 is met.
