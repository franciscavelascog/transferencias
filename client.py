from fintoc import Fintoc
import config


def get_client() -> Fintoc:
    """Initialize and return an authenticated Fintoc client with JWS signing."""
    return Fintoc(config.SECRET_KEY, jws_private_key=config.JWS_PRIVATE_KEY_PATH)
