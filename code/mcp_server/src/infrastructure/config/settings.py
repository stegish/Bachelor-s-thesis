from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """MCP Server settings"""
    
    # MongoDB Configuration
    mongo_uri: str = Field(..., alias='MONGO_URI')
    database_name: str = Field(default='manufacturing_db', alias='DATABASE_NAME')
    
    # AI Manager DB Configuration
    ai_manager_db_uri: str = Field(..., alias='AI_MANAGER_DB_URI')
    ai_manager_db_name: str = Field(default='AI-manager', alias='AI_MANAGER_DB_NAME')
    
    # Server Configuration
    port: int = Field(default=5002, alias='PORT')
    host: str = Field(default='0.0.0.0', alias='HOST')
    log_level: str = Field(default='INFO', alias='LOG_LEVEL')
    
    # MCP Configuration
    server_name: str = 'manufacturing-mcp-server'
    server_version: str = '1.0.0'
    
    model_config = {
        'env_file': '.env',
        'case_sensitive': False,
        'populate_by_name': True
    }