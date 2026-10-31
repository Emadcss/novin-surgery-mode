from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://novin:novin@localhost:5432/novin_kiosk"
    secret_key: str = "change-me"
    token_ttl_minutes: int = 12 * 60
    kiosk_key: str = ""
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "tauri://localhost",
    ]
    media_dir: Path = Path("media")
    timezone: str = "Asia/Tehran"
    bcrypt_rounds: int = 12
    login_max_failures: int = 5
    login_lock_seconds: int = 300
    seed_admin_name: str = "مدیر کل"
    seed_admin_pin: str = "1234"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
