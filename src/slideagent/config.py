from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SLIDEAGENT_",
        extra="ignore",
    )

    openai_api_key: str = Field(default="", json_schema_extra={"env": "OPENAI_API_KEY"})

    max_concurrency: int = 5
    max_retries: int = 3
    image_quality: str = "low"
    image_size: str = "1024x1024"

    image_model: str = "gpt-image-2"

    @classmethod
    def settings_customise_sources(cls, settings_cls, **kwargs):
        """Allow OPENAI_API_KEY without prefix alongside prefixed vars."""
        from pydantic_settings import DotEnvSettingsSource, EnvSettingsSource

        return (
            EnvSettingsSource(settings_cls, env_prefix="SLIDEAGENT_"),
            EnvSettingsSource(settings_cls, env_prefix=""),
            DotEnvSettingsSource(settings_cls, env_file=".env", env_prefix="SLIDEAGENT_"),
            DotEnvSettingsSource(settings_cls, env_file=".env", env_prefix=""),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
