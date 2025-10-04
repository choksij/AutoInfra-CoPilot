from __future__ import annotations

import hmac
import hashlib
from typing import Optional

from ..config.settings import get_settings


def verify_github_signature(body: bytes, signature_header: Optional[str]) -> bool:
    s = get_settings()
    secret = (s.github_webhook_secret or "").encode("utf-8")

    # If no secret configured, accept (dev/hackathon convenience)
    if not secret:
        return True

    if not signature_header:
        return False

    # signature_header format: "sha256=<hex>"
    try:
        scheme, their_sig = signature_header.split("=", 1)
    except ValueError:
        return False
    if scheme != "sha256" or not their_sig:
        return False

    mac = hmac.new(secret, msg=body, digestmod=hashlib.sha256)
    expected = mac.hexdigest()

    # constant-time compare
    return hmac.compare_digest(expected, their_sig)
