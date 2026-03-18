import math
import time
import uuid
from typing import Any

import config
from client import get_client


def split_amount(total: int, max_chunk: int = config.MAX_TRANSFER_AMOUNT) -> list[int]:
    """Split a total amount into chunks respecting the per-transfer limit."""
    n_full = total // max_chunk
    remainder = total % max_chunk
    chunks = [max_chunk] * n_full
    if remainder:
        chunks.append(remainder)
    return chunks


def create_transfers(total_amount: int, counterparty: dict) -> list[dict]:
    """
    Split total_amount into legal chunks and create one transfer per chunk.
    Returns a list of transfer result dicts.
    """
    client = get_client()
    chunks = split_amount(total_amount)
    n = len(chunks)

    print(f"\nTotal a transferir: ${total_amount:,} CLP")
    print(f"Transferencias a crear: {n} (máx. ${config.MAX_TRANSFER_AMOUNT:,} CLP cada una)\n")

    results = []
    for i, amount in enumerate(chunks, start=1):
        idempotency_key = str(uuid.uuid4())
        comment = f"Lote {i}/{n}"

        print(f"[{i}/{n}] Creando transferencia de ${amount:,} CLP... ", end="", flush=True)
        try:
            transfer = client.v2.transfers.create(
                idempotency_key=idempotency_key,
                account_id=config.ACCOUNT_ID,
                amount=amount,
                currency=config.CURRENCY,
                comment=comment,
                counterparty=counterparty,
            )
            results.append({
                "id": transfer.id,
                "batch_number": i,
                "amount": amount,
                "comment": comment,
                "status": transfer.status,
                "counterparty_name": counterparty.get("holder_name"),
                "counterparty_account": counterparty.get("account_number"),
                "institution_id": counterparty.get("institution_id"),
                "idempotency_key": idempotency_key,
                "error": None,
            })
            print(f"OK (id: {transfer.id})")
        except Exception as e:
            results.append({
                "id": None,
                "batch_number": i,
                "amount": amount,
                "comment": comment,
                "status": "creation_failed",
                "counterparty_name": counterparty.get("holder_name"),
                "counterparty_account": counterparty.get("account_number"),
                "institution_id": counterparty.get("institution_id"),
                "idempotency_key": idempotency_key,
                "error": str(e),
            })
            print(f"ERROR: {e}")

    return results


def poll_final_statuses(results: list[dict], poll_interval: int = 3, max_retries: int = 10) -> list[dict]:
    """
    Poll transfers that are still pending until they reach a terminal status
    or max_retries is exhausted.
    Terminal statuses: succeeded, failed, rejected, returned.
    """
    TERMINAL = {"succeeded", "failed", "rejected", "returned", "creation_failed"}
    client = get_client()

    pending = [r for r in results if r["id"] and r["status"] not in TERMINAL]
    if not pending:
        return results

    print(f"\nEsperando estado final para {len(pending)} transferencia(s) pendiente(s)...")

    for attempt in range(1, max_retries + 1):
        still_pending = [r for r in pending if r["status"] not in TERMINAL]
        if not still_pending:
            break

        print(f"  Intento {attempt}/{max_retries} — consultando {len(still_pending)} transferencia(s)...")
        for result in still_pending:
            try:
                transfer = client.v2.transfers.get(result["id"])
                result["status"] = transfer.status
            except Exception as e:
                print(f"    Advertencia: no se pudo consultar {result['id']}: {e}")

        if any(r["status"] not in TERMINAL for r in still_pending):
            time.sleep(poll_interval)

    return results
