from functools import lru_cache
from typing import Optional

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = Field(default="development")
    run_sync: bool = Field(default=True, alias="RUN_SYNC")

    sample_tf_path: str = Field(default="backend/sample/tf", alias="SAMPLE_TF_PATH")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", alias="LLM_MODEL")

    dd_api_key: str = Field(default="", alias="DD_API_KEY")
    dd_app_key: str = Field(default="", alias="DD_APP_KEY")
    dd_site: str = Field(default="us5.datadoghq.com", alias="DD_SITE")

    clickhouse_url: Optional[AnyUrl] = Field(default=None, alias="CLICKHOUSE_URL")
    clickhouse_user: str = Field(default="default", alias="CLICKHOUSE_USER")
    clickhouse_password: str = Field(default="", alias="CLICKHOUSE_PASSWORD")

    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    github_webhook_secret: str = Field(default="", alias="GITHUB_WEBHOOK_SECRET")

    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
