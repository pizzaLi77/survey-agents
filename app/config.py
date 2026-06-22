from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    java_base_url: str = "http://127.0.0.1:8080"
    internal_token: str = "dev-token"
    request_timeout_seconds: float = 10.0
    llm_base_url: str = "https://api.deepseek.com"
    llm_api_key: str | None = None
    llm_model: str = "deepseek-chat"
    llm_temperature: float = 0.1
    llm_max_retries: int = 2


settings = Settings()
