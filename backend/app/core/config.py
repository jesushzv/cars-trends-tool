"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    PROJECT_NAME: str = "Car Trends Analysis Tool"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/car_trends"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Scraping
    SCRAPING_DELAY_MIN: int = 1
    SCRAPING_DELAY_MAX: int = 3
    MAX_RETRIES: int = 3
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # Facebook Marketplace (optional authentication)
    FB_EMAIL: Optional[str] = None
    FB_PASSWORD: Optional[str] = None
    
    # Redis (for caching)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Location settings
    TARGET_LOCATION: str = "Tijuana, Mexico"
    TARGET_RADIUS_KM: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
