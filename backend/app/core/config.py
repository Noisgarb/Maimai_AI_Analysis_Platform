from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Maimai Platform API"
    app_env: str = Field(default="dev")
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    diving_fish_base_url: str = "https://www.diving-fish.com/api/maimaidxprober"
    diving_fish_developer_token: str = ""
    diving_fish_import_token: str = ""
    diving_fish_timeout_seconds: int = 15

    ai_provider: str = "mock"
    ai_api_base: str = ""
    ai_api_key: str = ""
    ai_model: str = "mock-model"

    db_url: str = "sqlite+aiosqlite:///./maimai.db"


settings = Settings()
