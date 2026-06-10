"""Slack incoming-webhook helper (#bizoo-seo, #bizoo-crm)."""

import requests


def post_slack(webhook_url, text):
    """Post text to a Slack incoming webhook.

    Returns True when posted. When the webhook is unset (local testing before
    Slack is wired), prints a note and returns False instead of failing.
    """
    if not webhook_url:
        print("[slack] webhook not configured, skipping post")
        return False
    resp = requests.post(webhook_url, json={"text": text}, timeout=15)
    resp.raise_for_status()
    return True
