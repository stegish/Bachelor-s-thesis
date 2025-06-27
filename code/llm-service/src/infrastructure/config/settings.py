# src/infrastructure/config/settings.py
from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    """Application settings following 12-factor app principles"""
    
    # API Keys
    anthropic_api_key: str = Field(..., env='ANTHROPIC_API_KEY')
    
    # Model Configuration
    model_name: str = Field('claude-3-sonnet-20240229', env='MODEL_NAME')
    max_tokens: int = Field(4096, env='MAX_TOKENS')
    temperature: float = Field(0.7, env='TEMPERATURE')
    
    # MongoDB Configuration
    mongo_uri: str = Field(..., env='MONGO_URI')
    database_name: str = Field('manufacturing_db', env='DATABASE_NAME')
    
    # Application Configuration
    app_name: str = 'manufacturing-llm-service'
    app_version: str = '1.0.0'
    environment: str = Field('production', env='FLASK_ENV')
    debug: bool = Field(False)
    
    # File Upload Configuration
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: set = {'csv', 'txt'}
    temp_upload_folder: str = '/tmp/llm_uploads'
    
    class Config:
        env_file = '.env'
        case_sensitive = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary, hiding sensitive data"""
        data = self.dict()
        # Hide API key
        if 'anthropic_api_key' in data:
            data['anthropic_api_key'] = '***' + data['anthropic_api_key'][-4:]
        return data