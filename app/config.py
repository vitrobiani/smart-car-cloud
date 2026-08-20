from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # DB URL is consumed by smart_car_project/database.py, not by us directly.
    # Left here so the setting is discoverable; the adapter reads it via that package.
    redis_url: str = "redis://localhost:6379/0"

    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Local llama-server (OpenAI-compatible). See run-local-llm.sh.
    llm_base_url: str = "http://127.0.0.1:8880/v1"
    llm_model: str = "gemma"
    llm_timeout_s: float = 60.0

    log_level: str = "INFO"


settings = Settings()
