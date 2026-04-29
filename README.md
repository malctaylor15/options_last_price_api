# Options Last Price API

FastAPI service that returns option prices and upcoming earnings dates using Yahoo Finance data.

## What this repo contains

* **API service**: FastAPI app with endpoints for option prices and earnings dates.
* **Security**: API key authentication using the system keyring (no plaintext secrets).
* **Integration helpers**: Google Sheets Apps Script for calling the API.
* **Deployment example**: A systemd unit template for running the service.
* **Notebooks**: Local experimentation and testing.

## Quick start

```bash
pip install -r requirements.txt
python scripts/set_api_key.py
python -m uvicorn options_last_price_api.main:app --app-dir src --reload --host 127.0.0.1 --port 2524
```

Then visit `http://127.0.0.1:2524/docs` or call the endpoints with your API key:

```bash
curl -H "X-API-Key: <your-key>" \
  "http://127.0.0.1:2524/option-price/AAPL251219C00200000"
```

## Repository map

```
archive/        Retired source files kept for reference
deploy/         Example service definitions
docs/           Documentation (file map, key management)
integrations/   External integrations (Google Sheets script)
notebooks/      Local experimentation notebooks
scripts/        Local CLI utilities
src/            Application source code
```

## API key storage

The API key is stored in your system keyring (no plaintext files). Use:

```bash
python scripts/set_api_key.py
```

If you need a temporary override, set the environment variable `OPTIONS_API_KEY` in your shell or process manager.

## Documentation

* `docs/file-map.md` explains where to find key files.
* `docs/key-management.md` explains API key storage and rotation.
* `docs/system-service.md` shows how to run the API with systemd, check service status, and test with curl/Python.

## Deployment notes

An example systemd unit lives at `deploy/options_last_price.service`. It assumes the app code lives in
`/home/malcolm/options_last_price_api/src`. Update paths as needed.
