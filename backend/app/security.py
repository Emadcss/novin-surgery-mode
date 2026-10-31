import time
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings

ALGO = "HS256"


def hash_pin(pin: str) -> str:
    return bcrypt.hashpw(pin.encode(), bcrypt.gensalt(rounds=settings.bcrypt_rounds)).decode()


def verify_pin(pin: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(pin.encode(), hashed.encode())
    except ValueError:
        return False


def create_token(admin_id: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(admin_id), "iat": now, "exp": now + timedelta(minutes=settings.token_ttl_minutes)}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGO)


def decode_token(token: str) -> int | None:
    try:
        data = jwt.decode(token, settings.secret_key, algorithms=[ALGO])
        return int(data["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


class LoginLimiter:
    """قفل ساده‌ی تلاش ناموفق بر اساس IP (در حافظه؛ برای چند پردازه به Redis منتقل شود)."""

    def __init__(self) -> None:
        self._fails: dict[str, list[float]] = {}

    def _recent(self, key: str) -> list[float]:
        cutoff = time.monotonic() - settings.login_lock_seconds
        lst = [t for t in self._fails.get(key, []) if t > cutoff]
        self._fails[key] = lst
        return lst

    def locked(self, key: str) -> bool:
        return len(self._recent(key)) >= settings.login_max_failures

    def fail(self, key: str) -> None:
        self._recent(key).append(time.monotonic())

    def ok(self, key: str) -> None:
        self._fails.pop(key, None)

    def reset(self) -> None:
        self._fails.clear()


limiter = LoginLimiter()
