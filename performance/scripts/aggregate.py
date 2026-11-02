"""Builds performance/results/aggregate.csv from results.jtl and checks the NFR thresholds.

The columns match JMeter's Aggregate Report listener. Percentiles use the nearest-rank method,
the same as JMeter.

Usage (from the project root):
    python performance/scripts/aggregate.py
    python performance/scripts/aggregate.py --jtl performance/results/results.jtl --out performance/results/aggregate.csv
"""
import argparse
import csv
import math
from pathlib import Path

PERF = Path(__file__).resolve().parent.parent
# NFR id -> (label, P95 limit in ms); NFR-03 is the overall error-rate limit in percent.
NFR_P95 = {"NFR-01": ("Login page", 3000), "NFR-02": ("Products page", 4000)}
NFR_ERROR_LIMIT = 2.0


def percentile(sorted_values, pct):
    rank = max(1, math.ceil(pct / 100 * len(sorted_values)))
    return sorted_values[rank - 1]


def summarise(rows):
    times = sorted(int(r["elapsed"]) for r in rows)
    errors = sum(r["success"] != "true" for r in rows)
    start = min(int(r["timeStamp"]) for r in rows)
    end = max(int(r["timeStamp"]) + int(r["elapsed"]) for r in rows)
    seconds = max((end - start) / 1000, 0.001)
    received = sum(int(r.get("bytes") or 0) for r in rows)
    sent = sum(int(r.get("sentBytes") or 0) for r in rows)
    return {
        "# Samples": len(rows),
        "Average": round(sum(times) / len(times)),
        "Median": percentile(times, 50),
        "90% Line": percentile(times, 90),
        "95% Line": percentile(times, 95),
        "99% Line": percentile(times, 99),
        "Min": times[0],
        "Max": times[-1],
        "Error %": f"{100 * errors / len(rows):.2f}%",
        "Throughput": f"{len(rows) / seconds:.2f}/sec",
        "Received KB/sec": f"{received / 1024 / seconds:.2f}",
        "Sent KB/sec": f"{sent / 1024 / seconds:.2f}",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--jtl", default=PERF / "results" / "results.jtl")
    parser.add_argument("--out", default=PERF / "results" / "aggregate.csv")
    args = parser.parse_args()

    with open(args.jtl, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    labels = sorted({r["label"] for r in rows})
    table = [{"Label": label, **summarise([r for r in rows if r["label"] == label])} for label in labels]
    table.append({"Label": "TOTAL", **summarise(rows)})

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)
    print(f"wrote {args.out}")
    for row in table:
        print(f"  {row['Label']:<15} samples={row['# Samples']:<5} avg={row['Average']}ms "
              f"p95={row['95% Line']}ms max={row['Max']}ms errors={row['Error %']}")

    by_label = {row["Label"]: row for row in table}
    print("NFR check:")
    for nfr, (label, limit) in NFR_P95.items():
        p95 = by_label[label]["95% Line"]
        print(f"  {nfr} {label} P95 {p95} ms < {limit} ms: {'PASS' if p95 < limit else 'FAIL'}")
    error_pct = float(by_label["TOTAL"]["Error %"].rstrip("%"))
    print(f"  NFR-03 error rate {error_pct:.2f}% < {NFR_ERROR_LIMIT}%: "
          f"{'PASS' if error_pct < NFR_ERROR_LIMIT else 'FAIL'}")


if __name__ == "__main__":
    main()
