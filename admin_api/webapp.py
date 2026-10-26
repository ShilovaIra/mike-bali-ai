from __future__ import annotations

import hashlib
import hmac
import json
from urllib.parse import parse_qsl


def telegram_user(init_data: str, bot_token: str) -> dict | None:
    parsed = dict(parse_qsl(init_data, keep_blank_values=True))
    received = parsed.pop("hash", None)
    if not received or not bot_token:
        return None
    data_check = "\n".join(f"{key}={value}" for key, value in sorted(parsed.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    calculated = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(calculated, received):
        return None
    raw_user = parsed.get("user")
    if not raw_user:
        return None
    try:
        user = json.loads(raw_user)
    except json.JSONDecodeError:
        return None
    if not isinstance(user, dict) or "id" not in user:
        return None
    return user
