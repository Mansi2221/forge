from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Forge API"
    debug: bool = False

    anthropic_api_key: str = ""
    openai_api_key: str = ""

    database_url: str = "postgresql://localhost:5432/forge"

    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
