"""Configuration management for Agent Composer backend."""

from functools import lru_cache
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = "Agent Composer"
    debug: bool = False
    log_level: str = "INFO"

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS settings (comma-separated string in env, converted to list)
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Database settings
    database_url: str = "sqlite+aiosqlite:///./agent_composer.db"

    # LLM Provider API Keys (optional - can be configured via UI)
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    openrouter_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"

    # Default models
    default_openai_model: str = "gpt-4o"
    default_anthropic_model: str = "claude-3-5-sonnet-20241022"
    default_openrouter_model: str = "anthropic/claude-3.5-sonnet"
    default_ollama_model: str = "llama3.2"

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.openai_api_key)

    def has_anthropic_key(self) -> bool:
        """Check if Anthropic API key is configured."""
        return bool(self.anthropic_api_key)

    def validate_required_keys(self) -> list[str]:
        """Return list of missing but commonly needed API keys."""
        missing = []
        if not self.openai_api_key:
            missing.append("OPENAI_API_KEY")
        if not self.anthropic_api_key:
            missing.append("ANTHROPIC_API_KEY")
        return missing


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
