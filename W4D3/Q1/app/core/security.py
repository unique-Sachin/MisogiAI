import hashlib
import secrets


HASH_ALGORITHM = "sha256"
_KEY_LEN_BYTES = 32


def generate_api_key() -> str:
    """Generate a random 32-byte hex API key."""
    return secrets.token_hex(_KEY_LEN_BYTES)


def hash_api_key(raw_key: str) -> str:
    """Return the SHA-256 hash of the raw key (hex)."""
    return hashlib.sha256(raw_key.encode()).hexdigest()


def verify_api_key(raw_key: str, hashed: str) -> bool:
    return hash_api_key(raw_key) == hashed 