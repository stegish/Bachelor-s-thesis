from typing import Dict, Any
from dependency_injector import containers, providers
from ..external import AnthropicLLMService, MCPClient
from ..persistence import MongoDBContextRepository
from ...application.use_cases import *
from .settings import Settings

class Container(containers.DeclarativeContainer):
    """DI Container following Dependency Inversion Principle"""
    
    # Configuration
    config = providers.Configuration()
    settings = providers.Singleton(Settings)
    
    # Infrastructure services
    llm_service = providers.Singleton(
        AnthropicLLMService,
        settings=settings
    )
    
    mcp_client = providers.Singleton(
        MCPClient,
        mcp_server_url=config.mcp.server_url
    )
    
    context_repository = providers.Singleton(
        MongoDBContextRepository,
        connection_string=config.mongodb.uri,
        database_name=config.mongodb.database
    )
    
    # Application services
    prompt_builder = providers.Singleton(PromptBuilder)
    context_enricher = providers.Singleton(ContextEnricher)
    
    # Use cases
    analyze_data_use_case = providers.Factory(
        AnalyzeDataUseCase,
        llm_service=llm_service,
        context_repository=context_repository,
        prompt_builder=prompt_builder,
        context_enricher=context_enricher
    )
    
    chat_use_case = providers.Factory(
        ChatUseCase,
        llm_service=llm_service,
        context_repository=context_repository
    )
    
    execute_mcp_action_use_case = providers.Factory(
        ExecuteMCPActionUseCase,
        mcp_client=mcp_client,
        llm_service=llm_service
    )