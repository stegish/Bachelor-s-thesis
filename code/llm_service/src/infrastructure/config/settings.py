from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    """Application settings following 12-factor app principles"""
    
    # AI Manager Database Configuration (ADD THESE)
    ai_manager_db_uri: Optional[str] = Field(default=None, alias='AI_MANAGER_DB_URI')
    ai_manager_db_name: str = Field(default='AI-manager', alias='AI_MANAGER_DB_NAME')


    # API Keys
    anthropic_api_key: str = Field(..., alias='ANTHROPIC_API_KEY')
    
    # Model Configuration
    model_name: str = Field(default='claude-3-sonnet-20240229', alias='MODEL_NAME')
    max_tokens: int = Field(default=4096, alias='MAX_TOKENS')
    temperature: float = Field(default=0.7, alias='TEMPERATURE')
    
    # MongoDB Configuration
    mongo_uri: str = Field(..., alias='MONGO_URI')
    database_name: str = Field(default='orders_db', alias='DATABASE_NAME')
    
    # Analytics Service Configuration (ADD THIS)
    analytics_service_url: str = Field(default='http://analytics_api:5000', alias='ANALYTICS_SERVICE_URL')


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
    
    @property
    def get_ai_manager_uri(self) -> str:
        """Get AI Manager DB URI, defaults to main MongoDB if not specified"""
        return self.ai_manager_db_uri or self.mongo_uri