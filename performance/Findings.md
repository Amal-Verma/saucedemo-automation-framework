# Performance Findings: SauceDemo (JMeter)

## Test setup

| Item | Value |
|---|---|
| Test plan | `performance/jmx/saucedemo_weekend_lab.jmx` |
| Target | https://www.saucedemo.com/ |
| Load profile | 20 concurrent users, 60 s ramp-up, 180 s duration |
| Think time | Uniform random 0 to 500 ms between pages |
| Pages per iteration | "Login page", then "Products page" (one transaction each) |
| Run date | 2026-11-01, JMeter 5.6.3 (non-GUI), OpenJDK 17 |
| Load generator | one laptop on a home internet connection (India; requests served by the GitHub Pages edge in Central India) |
| Results | `results/results.jtl`, `results/aggregate.csv`, dashboard `html_report/index.html` |

How the pages are measured (SauceDemo is a single-page React app on GitHub Pages):

- **Login page:** `GET /` plus its embedded CSS, JS bundle and favicon. Logging in itself is
  checked by JavaScript in the browser and sends no HTTP request, so the login page load is the
  server-side part of logging in.
- **Products page:** `GET /inventory.html`, which by design returns HTTP 404 with a small redirect
  page (asserted as expected, not counted as an error), then `GET /?/inventory.html` with its embedded
  resources, which is the chain a browser follows.
- Cookies and the HTTP cache are cleared at the start of every iteration, so each iteration acts as
  a new visitor: the login page downloads the full 538 KB JS bundle. The products page then reuses the
  cached bundle, as a real browser would.

## Results (aggregate.csv)

| Label | Samples | Average (ms) | Median (ms) | 90% (ms) | **95% (ms)** | 99% (ms) | Max (ms) | Error % | Throughput |
|---|---|---|---|---|---|---|---|---|---|
| Login page | 2117 | 654 | 290 | 1726 | **3869** | 4468 | 6906 | 0.00% | 11.60/s |
| Products page | 2099 | 34 | 16 | 63 | **140** | 259 | 4791 | 0.00% | 11.72/s |
| TOTAL | 4216 | 345 | 104 | 543 | 1751 | 4339 | 6906 | **0.00%** | 23.10/s |

## NFR verdicts

| NFR | Requirement | Measured | Result |
|---|---|---|---|
| NFR-01 | Login page P95 < 3.0 s (20 users) | P95 = **3.87 s** | **FAIL** |
| NFR-02 | Products page P95 < 4.0 s (20 users) | P95 = **0.14 s** | **PASS** |
| NFR-03 | Overall error rate < 2% | **0.00%** (0 of 4216 samples) | **PASS** |

## Notes and analysis

**NFR-01 fails, and the cause appears to be download bandwidth, not server processing.**
Login page P95 by phase of the test:

| Time window | Active users | Samples | Login P95 | Login average |
|---|---|---|---|---|
| 0 to 20 s | up to 7 | 88 | 0.52 s | 0.14 s |
| 20 to 40 s | up to 14 | 164 | 3.58 s | 0.54 s |
| 40 to 60 s | up to 20 | 269 | 3.37 s | 0.51 s |
| 60 to 120 s | 20 | 822 | 4.07 s | 0.73 s |
| 120 to 185 s | 20 | 774 | 3.90 s | 0.71 s |

- Each login page load transfers about 585 KB (mostly the JS bundle). At 20 users the test pulled
  about 6.8 MB/s in total, and the slow tail grew as more users downloaded at the same time.
- The products page, which uses the cached bundle and transfers only a few KB, stayed fast
  (P95 0.14 s) at full load. This suggests the server itself answers quickly, and the extra
  time on the login page is spent transferring the bundle over the tester's connection.
- The median login time stayed low (0.29 s), so most users were fast; NFR-01 fails on the
  slowest 5% of loads.
- A follow-up single download of the same bundle took 5.1 s at about 107 KB/s, which shows the
  connection's speed varies; the network speed was not controlled during the test.

**Recommendation:** rerun the test from a machine with a fast, wired, dedicated connection
(or a cloud load generator) before treating NFR-01 as a defect of the site. If it still fails
there, the fix is on the site side: compress and split the JS bundle so the first page needs
less than its current 538 KB.

**Other observations**
- 3 of 4216 samples have a response time of 0 ms. They are transactions that were cut off when the
  3-minute scheduler stopped the threads mid-iteration; they are not errors and do not change the P95.
- No HTTP errors, timeouts or failed assertions occurred during the run.
- Results depend on the network between the load generator and GitHub Pages, so they will
  differ between machines and runs.
