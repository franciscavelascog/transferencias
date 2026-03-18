import csv
import json
import os
from datetime import datetime


REPORTS_DIR = "reports"


def _ensure_reports_dir():
    os.makedirs(REPORTS_DIR, exist_ok=True)


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_csv(results: list[dict]) -> str:
    _ensure_reports_dir()
    path = os.path.join(REPORTS_DIR, f"transfers_{_timestamp()}.csv")
    fieldnames = [
        "batch_number", "id", "amount", "comment", "status",
        "counterparty_name", "counterparty_account", "institution_id",
        "idempotency_key", "error",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    return path


def save_json(results: list[dict]) -> str:
    _ensure_reports_dir()
    path = os.path.join(REPORTS_DIR, f"transfers_{_timestamp()}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    return path


def print_summary(results: list[dict]):
    from collections import Counter
    statuses = Counter(r["status"] for r in results)
    total_attempted = sum(r["amount"] for r in results)
    total_succeeded = sum(r["amount"] for r in results if r["status"] == "succeeded")

    print("\n" + "=" * 50)
    print("RESUMEN DE TRANSFERENCIAS")
    print("=" * 50)
    print(f"  Total transferencias : {len(results)}")
    print(f"  Monto total intentado: ${total_attempted:,} CLP")
    print(f"  Monto total exitoso  : ${total_succeeded:,} CLP")
    print("\n  Estados:")
    for status, count in statuses.items():
        print(f"    {status}: {count}")
    print("=" * 50)
