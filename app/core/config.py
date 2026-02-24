"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "sqlite:///./voting_system.db"

    # JWT
    JWT_SECRET_KEY: str = "change-this-super-secret-jwt-key-in-production"
    JWT_REFRESH_SECRET_KEY: str = "change-this-refresh-secret-key-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # HMAC Secret for Vote Anonymity
    HMAC_SECRET_KEY: str = "change-this-hmac-secret-key-in-production"

    # Application
    APP_NAME: str = "Secure Voting Platform"
    DEBUG: bool = False

    # Super Admin Seed
    SUPER_ADMIN_EMAIL: str = "admin@votingplatform.com"
    SUPER_ADMIN_PASSWORD: str = "Admin@123456"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
