from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Restaurant Voice Agent API"
    app_env: str = "development"
    log_level: str = "INFO"
    port: int = 8000
    cors_origins: str = "http://localhost:3000"
    
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "restaurant_voice_assistant"
    mongodb_test_database: str = "restaurant_voice_assistant_test"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
