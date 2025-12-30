# File map

This repo is intentionally small. Use this map to locate the right files quickly.

## Runtime code

* `src/options_last_price_api/main.py`: FastAPI app, endpoints, and data helpers.
* `src/options_last_price_api/security.py`: API key lookup and authentication dependency.

## Local utilities

* `scripts/set_api_key.py`: Stores the API key in the system keyring.

## Integrations & operations

* `integrations/google_sheets_script.gs`: Google Sheets Apps Script helper.
* `deploy/options_last_price.service`: Example systemd service definition.

## Experiments and legacy

* `notebooks/`: Local notebooks for testing.
* `archive/`: Retired/legacy files kept for reference.
