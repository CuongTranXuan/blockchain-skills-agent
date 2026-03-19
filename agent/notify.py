from __future__ import annotations

import sys


def notify(message: str) -> None:
    """Send a notification to the human operator.

    Currently prints to stdout. Can be extended with Telegram, email, or
    webhook integrations.
    """
    border = "=" * 60
    print(f"\n{border}")
    print("[AGENT NOTIFICATION]")
    print(border)
    print(message)
    print(f"{border}\n")
    sys.stdout.flush()
