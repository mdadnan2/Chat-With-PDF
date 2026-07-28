from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    app_name: str
    app_version: str

    host: str
    port: int

    upload_dir: str

    google_api_key: str = ""
    database_url: str

    gemini_chat_model: str

    database_url: str

    jwt_secret_key: str = Field(alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
