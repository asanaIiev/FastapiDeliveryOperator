from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str 
    SECRET_KEY: str
    REFERSH_TOKEN_LIFETIME: int 
    ACCESS_TOKEN_LIFETIME: int 
    ALGORITHM: str
    ADMIN_USERNAME: str | None = None
    ADMIN_PASSWORD: str | None = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / '.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()