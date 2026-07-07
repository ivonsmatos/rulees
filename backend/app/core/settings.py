from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Rulees"
    environment: str = "development"
    database_url: str = "sqlite:///./rulees.db"
    secret_key: str = "change-me-before-sharing"
    access_token_expire_minutes: int = 1440
    frontend_origin: str = "http://127.0.0.1:5173"
    cors_extra_origins: str = Field(default="")
    stt_provider: str = "mock"
    stt_timeout_seconds: float = 20.0
    stt_diarize: bool = True
    deepgram_api_key: str = Field(default="", repr=False)
    deepgram_model: str = "nova-3"
    deepgram_language: str = "pt-BR"
    redis_url: str = "redis://127.0.0.1:6379/0"
    storage_path: str = "./storage"
    auto_create_tables: bool = True
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 240
    rate_limit_window_seconds: int = 60
    audit_retention_days: int = 365
    signed_url_expire_seconds: int = 300
    sentry_dsn: str = Field(default="", repr=False)
    opentelemetry_enabled: bool = True

    # P3 — LLM provider (heuristic | openai | ollama)
    llm_provider: str = Field(default="heuristic")
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="llama3")

    # RAG — provider de embeddings (deterministic | openai | ollama)
    embedding_provider: str = Field(default="deterministic")
    openai_api_key: str = Field(default="", repr=False)
    openai_model: str = Field(default="gpt-4o-mini")
    openai_base_url: str = Field(default="https://api.openai.com/v1")
    llm_timeout_seconds: float = Field(default=12.0)

    # P3 — Private/Self-hosted deployment
    deployment_mode: str = Field(default="saas")  # saas | private
    private_instance_name: str = Field(default="Rulees")
    disable_telemetry: bool = Field(default=False)
    disable_billing: bool = Field(default=False)

    # P3 — API pública
    public_api_enabled: bool = Field(default=True)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, value: str) -> str:
        normalized = value.lower().strip()
        allowed = {"development", "test", "staging", "production"}
        if normalized not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @field_validator("stt_provider")
    @classmethod
    def validate_stt_provider(cls, value: str) -> str:
        normalized = value.lower().strip()
        allowed = {"mock", "deepgram"}
        if normalized not in allowed:
            raise ValueError(f"STT_PROVIDER must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @field_validator("llm_provider")
    @classmethod
    def validate_llm_provider(cls, value: str) -> str:
        normalized = value.lower().strip()
        allowed = {"heuristic", "openai", "ollama"}
        if normalized not in allowed:
            raise ValueError(f"LLM_PROVIDER must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @field_validator("embedding_provider")
    @classmethod
    def validate_embedding_provider(cls, value: str) -> str:
        normalized = value.lower().strip()
        allowed = {"deterministic", "openai", "ollama"}
        if normalized not in allowed:
            raise ValueError(f"EMBEDDING_PROVIDER must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @field_validator("deployment_mode")
    @classmethod
    def validate_deployment_mode(cls, value: str) -> str:
        normalized = value.lower().strip()
        if normalized not in {"saas", "private"}:
            raise ValueError("DEPLOYMENT_MODE must be 'saas' or 'private'")
        return normalized

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.environment == "production" and self.secret_key == "change-me-before-sharing":
            raise ValueError("SECRET_KEY must be changed in production")
        return self

    @property
    def cors_origins(self) -> list[str]:
        origins = [self.frontend_origin, "http://localhost:5173"]
        if self.cors_extra_origins:
            origins.extend(
                origin.strip()
                for origin in self.cors_extra_origins.split(",")
                if origin.strip()
            )
        return list(dict.fromkeys(origins))

    @property
    def resolved_storage_path(self) -> Path:
        return Path(self.storage_path).expanduser().resolve()


@lru_cache
def get_settings() -> Settings:
    return Settings()
