"""Telegram initData верификация (HMAC-SHA256)."""
import hashlib
import hmac
import json
import urllib.parse

from core.config import settings
from core.exceptions import Unauthorized


def verify_init_data(x_tg_init_data: str) -> dict:
    """Проверяет подпись, возвращает dict c tg_user или бросает Unauthorized."""
    data = dict(urllib.parse.parse_qsl(x_tg_init_data))
    received_hash = data.pop("hash", "")

    data_check = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret = hmac.new(
        hmac.new(b"WebAppData", settings.telegram_bot_token.encode(), hashlib.sha256).digest(),
        data_check.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(secret, received_hash):
        raise Unauthorized("Invalid Telegram auth")

    tg_user = json.loads(data.get("user", "{}"))
    if not tg_user.get("id"):
        raise Unauthorized("No user in initData")

    return tg_user
