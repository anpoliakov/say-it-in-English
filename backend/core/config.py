from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    minio_endpoint: str
    minio_access_key: str
    minio_secret_key: str
    minio_bucket: str = "word-images"
    secret_key: str
    dev_mode: bool = True
    telegram_bot_token: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
