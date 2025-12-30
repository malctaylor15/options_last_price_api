from __future__ import annotations

from getpass import getpass
from pathlib import Path
import sys

import keyring

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))

from options_last_price_api.security import KEYRING_SERVICE, KEYRING_USERNAME


def main() -> None:
    api_key = getpass("Enter the API key to store: ").strip()
    if not api_key:
        raise SystemExit("API key cannot be empty.")
    confirm_key = getpass("Confirm the API key: ").strip()
    if api_key != confirm_key:
        raise SystemExit("API keys do not match.")
    keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, api_key)
    print("API key stored in the system keyring.")


if __name__ == "__main__":
    main()
