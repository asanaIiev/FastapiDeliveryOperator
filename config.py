from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_URL: str 
    SECRET_KEY: str
    REFERSH_TOKEN_LIFETIME: int 
    ACCESS_TOKEN_LIFETIME: int 
    ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()