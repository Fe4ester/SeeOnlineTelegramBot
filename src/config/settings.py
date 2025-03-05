from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    BOT_TOKEN: str
    EXTERNAL_SERVICE_API_URL: str
    REDIS_URL: str
    PRIVATE: bool
    BOT_WHITELIST: list[int]

    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8")


settings = Settings()
