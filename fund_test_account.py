"""
Simula una transferencia entrante para fondear la cuenta en modo Test.

Uso:
    python fund_test_account.py --amount 600000000

Solo funciona con llaves sk_test_. No mueve dinero real.
"""

import argparse
import requests
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("FINTOC_SECRET_KEY")
ACCOUNT_NUMBER_ID = "acno_3B3SiIpkFTwDulkhCXdfBGwIlTw"  # root account number id


def simulate_inbound(amount: int, currency: str = "CLP") -> dict:
    response = requests.post(
        "https://api.fintoc.com/v2/simulate/receive_transfer",
        headers={
            "Authorization": SECRET_KEY,
            "Content-Type": "application/json",
        },
        json={
            "account_number_id": ACCOUNT_NUMBER_ID,
            "amount": amount,
            "currency": currency,
        },
    )
    response.raise_for_status()
    return response.json()


def main():
    parser = argparse.ArgumentParser(description="Fondea la cuenta de prueba con una transferencia simulada.")
    parser.add_argument("--amount", type=int, default=600_000_000,
                        help="Monto a acreditar en CLP (default: 600000000)")
    args = parser.parse_args()

    print(f"Simulando ingreso de ${args.amount:,} CLP a la cuenta de prueba...")
    result = simulate_inbound(args.amount)
    print(f"  ✓ Transferencia simulada: {result['id']}")
    print(f"  Estado  : {result['status']}")
    print(f"  Monto   : ${result['amount']:,} {result['currency']}")
    print(f"  Dirección: {result['direction']}")
    print("\nCuenta lista para ejecutar transferencias de salida.")


if __name__ == "__main__":
    main()
