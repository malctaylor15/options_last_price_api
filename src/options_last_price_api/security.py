from __future__ import annotations

from functools import lru_cache
import os

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
import keyring
from keyring.errors import NoKeyringError

API_KEY_NAME = "X-API-Key"
API_KEY_ENV_VAR = "OPTIONS_API_KEY"
KEYRING_SERVICE = "options-last-price-api"
KEYRING_USERNAME = "default"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


@lru_cache
def get_configured_api_key() -> str | None:
    env_key = os.getenv(API_KEY_ENV_VAR)
    if env_key:
        return env_key
    return keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)


def get_api_key(api_key: str = Security(api_key_header)) -> str:
    try:
        configured_key = get_configured_api_key()
    except NoKeyringError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "No system keyring backend available. Configure a keyring backend "
                f"or set {API_KEY_ENV_VAR} for this process."
            ),
        )
    if not configured_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "API key not configured. Set it with the keyring helper script or "
                f"the {API_KEY_ENV_VAR} environment variable."
            ),
        )
    if api_key == configured_key:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key. Access denied.",
    )
