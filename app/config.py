from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    java_base_url: str = "http://127.0.0.1:8080"
    internal_token: str = "dev-token"
    request_timeout_seconds: float = 10.0


settings = Settings()
