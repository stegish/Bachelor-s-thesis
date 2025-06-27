from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings using Pydantic"""
    # Application
    app_name: str = "Manufacturing Analytics"
    app_version: str = "2.0.0"
    environment: str = "development"
    log_level: str = "INFO"
    
    # MongoDB
    mongo_uri: str = "mongodb://localhost:27017"
    database_name: str = "manufacturing_db"
    process_db_name: Optional[str] = None  # If None, uses database_name
    
    # Analytics
    output_directory: str = "./analytics_output"
    schedule_interval_minutes: int = 60
    
    # API
    api_prefix: str = "/api/v1"
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    def get_process_db_name(self) -> str:
        """Get process database name, defaults to main database if not specified"""
        return self.process_db_name or self.database_name
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        env_prefix = ""  # No prefix for environment variables

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()