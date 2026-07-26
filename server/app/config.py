from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str
    app_version: str

    host: str
    port: int

    upload_dir: str

    google_api_key: str = ""
    database_url: str

    gemini_chat_model: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
