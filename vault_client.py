"""
vault_client.py

Utility for fetching secrets from HashiCorp Vault.
The base path is expected to be stored in NOTION or environment variable.

Environment variables required
------------------------------
VAULT_ADDR   : Vault server URL
VAULT_TOKEN  : Token with read access
VAULT_BASE   : Base secret path, e.g. "secret/data/akari-value"

Example:
    from vault_client import get_secret
    slack_webhook = get_secret("slack/webhook_url")
"""

import os
from typing import Any

try:
    import hvac  # type: ignore
except ImportError:
    hvac = None  # Placeholder for environments without hvac


class VaultNotConfigured(Exception):
    """Raised when Vault connection information is missing or invalid."""


def _client():
    """Return an authenticated hvac.Client instance."""
    if hvac is None:
        raise ImportError("hvac library not installed")

    addr = os.getenv("VAULT_ADDR")
    token = os.getenv("VAULT_TOKEN")

    if not addr or not token:
        raise VaultNotConfigured("VAULT_ADDR / VAULT_TOKEN missing")

    client = hvac.Client(url=addr, token=token)
    if not client.is_authenticated():
        raise VaultNotConfigured("Vault authentication failed")
    return client


def get_secret(relative_path: str) -> Any:
    """Fetch secret at VAULT_BASE/relative_path."""
    base = os.getenv("VAULT_BASE", "secret/data/akari-value")
    # Ensure single slash between base and relative path
    full_path = f"{base.rstrip('/')}/{relative_path.lstrip('/') }"

    client = _client()
    response = client.secrets.kv.v2.read_secret_version(path=full_path)
    return response["data"]["data"]


if __name__ == "__main__":
    import sys, json

    if len(sys.argv) < 2:
        print("Usage: python vault_client.py <relative_path>")
        sys.exit(1)

    key = sys.argv[1]
    print(json.dumps(get_secret(key), ensure_ascii=False, indent=2))
