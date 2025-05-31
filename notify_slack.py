"""
notify_slack.py

Send a message to Slack using Incoming Webhook URL stored in Vault.

Vault keys
----------
slack/webhook_url : Incoming Webhook URL
slack/channel     : Target channel name (optional)

Usage:
    python notify_slack.py "メッセージ本文"
    # 例: SLACK_CHANNEL="#my-channel" python notify_slack.py "Hello"
"""

import json
import os
import sys
from typing import Optional

import requests  # type: ignore

from vault_client import get_secret


def post_message(text: str, channel: Optional[str] = None) -> None:
    """Send `text` to Slack via Incoming Webhook."""
    secret = get_secret("slack/webhook_url")
    webhook_url = secret if isinstance(secret, str) else secret.get("webhook_url")
    if not webhook_url:
        raise ValueError("Webhook URL not found in Vault")

    payload = {"text": text}
    if channel:
        payload["channel"] = channel

    response = requests.post(
        webhook_url,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    response.raise_for_status()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python notify_slack.py \"メッセージ\"")
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    # チャンネル名は環境変数優先、なければ Vault から取得
    channel_name = os.getenv("SLACK_CHANNEL") or get_secret("slack/channel")

    post_message(message, channel_name)
    print("Sent to Slack:", message)
