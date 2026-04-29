# Run as a systemd service

This guide shows how to run the Options Last Price API as a managed Linux system service using `systemd`.

## 1) Prerequisites

* Linux host with `systemd`.
* Python environment with project dependencies installed.
* API key already stored in keyring (or provided by environment variable).

## 2) Prepare paths and user

The sample unit file is at `deploy/options_last_price.service`.

Before installing it, confirm and update these fields to match your machine:

* `User=` and `Group=`
* `WorkingDirectory=`
* `ExecStart=`
* `Environment=PYTHONPATH=...`

The included example uses `/home/malcolm/options_last_price_api/src` paths, which you should replace with your own checkout path.

## 3) Install the unit

From the repository root:

```bash
sudo cp deploy/options_last_price.service /etc/systemd/system/options-last-price.service
sudo systemctl daemon-reload
```

## 4) Enable and start

```bash
sudo systemctl enable --now options-last-price.service
```

## 5) Check service status and logs

Check high-level status:

```bash
sudo systemctl status options-last-price.service
```

Follow logs in real time:

```bash
sudo journalctl -u options-last-price.service -f
```

Restart after config changes:

```bash
sudo systemctl restart options-last-price.service
```

## 6) Test the running service

Replace `YOUR_API_KEY` and adjust host/port if your unit binds differently.

### Test with curl

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  "http://127.0.0.1:2524/option-price/AAPL251219C00200000"
```

### Test with Python

```python
import requests

url = "http://127.0.0.1:2524/option-price/AAPL251219C00200000"
headers = {"X-API-Key": "YOUR_API_KEY"}

resp = requests.get(url, headers=headers, timeout=15)
print(resp.status_code)
print(resp.json())
```

## 7) Common troubleshooting notes

* **401 Unauthorized**: Verify the API key and header name `X-API-Key`.
* **Connection refused**: Service is not running, or host/port in unit file does not match your request URL.
* **Module import errors**: Re-check `PYTHONPATH` and `ExecStart` in the unit file.
* **Stale config after edits**: Run `sudo systemctl daemon-reload` and restart the service.
