# API key management

The API key is stored locally in your system keyring (no plaintext files).

## Set the key

```bash
python scripts/set_api_key.py
```

This writes the key to the OS keyring under the service name `options-last-price-api`.

If your environment does not provide a keyring backend, install one (for example,
`keyring` with a compatible backend) or use the temporary environment variable below.

## Rotate the key

Re-run the same command and overwrite the stored value.

## Temporary override (optional)

If you need a short-lived key (for CI or a one-off process), you can export:

```bash
export OPTIONS_API_KEY="your-key"
```

This does not write to any files and takes precedence over the keyring.
