from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, computed_field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",        
        env_file_encoding="utf-8",
        extra="ignore"          
    )

    TELEGRAM_BOT_TOKEN: str = "token"

    TELEGRAM_WEBHOOK_AUTH_KEY: str = "changethis"
    TELEGRAM_WEBHOOK_DOMAIN: str = "localhost"
    TELEGRAM_WEBHOOK_PORT: int = 443

    @property
    def TELEGRAM_WEBHOOK_URL(self):
        if self.TELEGRAM_WEBHOOK_PORT != 443:
            return f"https://{self.TELEGRAM_WEBHOOK_DOMAIN}:{self.TELEGRAM_WEBHOOK_PORT}"
        return f"https://{self.TELEGRAM_WEBHOOK_DOMAIN}"

    DB_PATH: str = "./database.db"
    DB_TYPE: Literal["sqlite", "postgres"] = "sqlite"
    DB_CREATE_USER: bool = True

    DB_NAME: str = "app"
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_USER: str = "app"
    DB_PASSWORD: str = "changethis"

    TELEGRAM_ADMIN_ID: int = 0

    @computed_field
    @property
    def DATABASE_URI(self) -> str:
        if self.DB_TYPE == "sqlite":
            return f"sqlite+aiosqlite:///{self.DB_PATH}"
        elif self.DB_TYPE == "postgres":
            return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        else: return ""

settings = Settings()
