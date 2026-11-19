from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Forge API"
    debug: bool = False

    anthropic_api_key: str = ""
    openai_api_key: str = ""

    database_url: str = "postgresql://localhost:5432/forge"

    cors_origins: list[str] = ["http://localhost:3000"]

    llm_timeout: int = 30
    llm_max_retries: int = 2
    llm_default_model: str = "claude-sonnet-5-5"
    llm_max_tokens: int = 1024
    llm_temperature: float = 0.7

    rate_limit_rpm: int = 60

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
