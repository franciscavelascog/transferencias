"""
Fintoc Transfers - Script para transferir montos altos en lotes.

Uso:
    python main.py --amount 500000000 --holder-id 12345678-9 --holder-name "Juan Pérez" \
                   --account-number 123456789 --account-type checking_account \
                   --institution-id cl_banco_de_chile

Tipos de cuenta válidos: checking_account, sight_account
Institutions CL: cl_banco_de_chile, cl_banco_estado, cl_banco_santander, cl_banco_bci, etc.
"""

import argparse
import sys

import config
import batch
import reporter


DEFAULT_COUNTERPARTY = {
    "holder_id": "12345678-9",
    "holder_name": "Cliente Test",
    "account_number": "123456789",
    "account_type": "checking_account",
    "institution_id": "cl_banco_de_chile",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Transfiere un monto total a un destinatario en lotes de máx. $7.000.000 CLP."
    )
    parser.add_argument("--amount", type=int, default=500_000_000,
                        help="Monto total a transferir en CLP (default: 500000000)")
    parser.add_argument("--holder-id", default=DEFAULT_COUNTERPARTY["holder_id"],
                        help="RUT del destinatario (ej: 12345678-9)")
    parser.add_argument("--holder-name", default=DEFAULT_COUNTERPARTY["holder_name"],
                        help="Nombre completo del destinatario")
    parser.add_argument("--account-number", default=DEFAULT_COUNTERPARTY["account_number"],
                        help="Número de cuenta del destinatario")
    parser.add_argument("--account-type", default=DEFAULT_COUNTERPARTY["account_type"],
                        choices=["checking_account", "sight_account"],
                        help="Tipo de cuenta: checking_account o sight_account")
    parser.add_argument("--institution-id", default=DEFAULT_COUNTERPARTY["institution_id"],
                        help="ID de institución Fintoc (ej: cl_banco_de_chile)")
    parser.add_argument("--format", choices=["csv", "json", "both"], default="csv",
                        help="Formato del reporte de salida (default: csv)")
    return parser.parse_args()


def main():
    args = parse_args()

    # Validate config and JWS key
    try:
        config.validate_config()
    except (EnvironmentError, FileNotFoundError) as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    counterparty = {
        "holder_id": args.holder_id,
        "holder_name": args.holder_name,
        "account_number": args.account_number,
        "account_type": args.account_type,
        "institution_id": args.institution_id,
    }

    print(f"Destinatario : {counterparty['holder_name']} ({counterparty['holder_id']})")
    print(f"Cuenta       : {counterparty['account_number']} — {counterparty['institution_id']}")

    # Step 1: Create transfers
    results = batch.create_transfers(args.amount, counterparty)

    # Step 2: Poll for final statuses
    results = batch.poll_final_statuses(results)

    # Step 3: Generate report
    paths = []
    if args.format in ("csv", "both"):
        path = reporter.save_csv(results)
        paths.append(path)
        print(f"\nReporte CSV guardado en: {path}")
    if args.format in ("json", "both"):
        path = reporter.save_json(results)
        paths.append(path)
        print(f"Reporte JSON guardado en: {path}")

    # Step 4: Print summary
    reporter.print_summary(results)


if __name__ == "__main__":
    main()
