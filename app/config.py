from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "infra-pulse"
    app_version: str = "dev"
    api_key: str = "changeme"

    class Config:
        env_file = ".env"

settings = Settings()
