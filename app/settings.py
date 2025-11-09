from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    
    APP_NAME: str = "Deep Learner AI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    DATABASE_URL: str
    
    REDIS_URL: str
    
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    GOOGLE_API_KEY: str
    TAVILY_API_KEY: str | None = None
    
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    
    LANGSMITH_TRACING: bool = False
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_PROJECT: str = "deep-learner-ai"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
