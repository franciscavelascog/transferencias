import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("FINTOC_SECRET_KEY")
ACCOUNT_ID = os.getenv("FINTOC_ACCOUNT_ID")
JWS_PRIVATE_KEY_PATH = os.getenv("JWS_PRIVATE_KEY_PATH", "private_key.pem")

MAX_TRANSFER_AMOUNT = 7_000_000  # CLP legal limit per transfer
CURRENCY = "CLP"


def validate_config():
    missing = [k for k, v in {
        "FINTOC_SECRET_KEY": SECRET_KEY,
        "FINTOC_ACCOUNT_ID": ACCOUNT_ID,
    }.items() if not v]

    if missing:
        raise EnvironmentError(f"Missing required env vars: {', '.join(missing)}")

    if not os.path.exists(JWS_PRIVATE_KEY_PATH):
        raise FileNotFoundError(
            f"JWS private key not found at '{JWS_PRIVATE_KEY_PATH}'.\n"
            "Run: openssl genrsa -out private_key.pem 2048\n"
            "Then upload the public key to the Fintoc dashboard."
        )
