from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Application settings following 12-factor app principles"""
    
    # API Keys
    anthropic_api_key: str = Field(..., alias='ANTHROPIC_API_KEY')
    
    # Model Configuration
    model_name: str = Field(default='claude-3-sonnet-20240229', alias='MODEL_NAME')
    max_tokens: int = Field(default=4096, alias='MAX_TOKENS')
    temperature: float = Field(default=0.7, alias='TEMPERATURE')
    
    # MongoDB Configuration
    mongo_uri: str = Field(..., alias='MONGO_URI')
    database_name: str = Field(default='orders_db', alias='DATABASE_NAME')
    
    # MCP Configuration
    mcp_server_url: str = Field(default='http://mcp_server:5002', alias='MCP_SERVER_URL')
    
    # Application Configuration
    app_name: str = 'manufacturing-llm-service'
    app_version: str = '1.0.0'
    environment: str = Field(default='production', alias='ENVIRONMENT')
    debug: bool = Field(default=False, alias='DEBUG')
    log_level: str = Field(default='INFO', alias='LOG_LEVEL')
    
    # File Upload Configuration
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: set = {'csv', 'txt'}
    temp_upload_folder: str = '/tmp/llm_uploads'
    
    model_config = {
        'env_file': '.env',
        'case_sensitive': False,
        'populate_by_name': True,
        'protected_namespaces': ('settings_',)  # Added to suppress warning
    }
    
    def to_dict(self) -> dict:
        """Convert to dictionary, hiding sensitive data"""
        data = self.model_dump()
        # Hide API key
        if 'anthropic_api_key' in data:
            data['anthropic_api_key'] = '***' + data['anthropic_api_key'][-4:]
        return data