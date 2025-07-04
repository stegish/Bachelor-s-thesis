from typing import Dict, Any
from dependency_injector import containers, providers
from ..external import AnthropicLLMService, MCPClient, FileStorageService
from ..persistence import MongoDBContextRepository, MemoryChatRepository
from ...application.use_cases import *
from ...application.services import *
from .settings import Settings
from ..persistence.recommendation_repository import MongoRecommendationRepository
from ...application.use_cases.generate_recommendation import GenerateRecommendationUseCase


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

    recommendation_repository = providers.Singleton(
        MongoRecommendationRepository,
        connection_string=settings.provided.ai_manager_db_uri,
        database_name=settings.provided.ai_manager_db_name
    )
    
    mcp_client = providers.Singleton(
        MCPClient,
        mcp_server_url=settings.provided.mcp_server_url
    )
    
    context_repository = providers.Singleton(
        MongoDBContextRepository,
        connection_string=settings.provided.mongo_uri,
        database_name=settings.provided.database_name
    )
    
    chat_repository = providers.Singleton(MemoryChatRepository)
    
    file_storage = providers.Singleton(
        FileStorageService,
        upload_folder=settings.provided.temp_upload_folder
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
    
    process_csv_use_case = providers.Factory(
        ProcessCSVUseCase,
        llm_service=llm_service,
        prompt_builder=prompt_builder
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
    
    get_suggestions_use_case = providers.Factory(
        GetSuggestionsUseCase,
        llm_service=llm_service
    )

    generate_recommendation_use_case = providers.Factory(
        GenerateRecommendationUseCase,
        llm_service=llm_service,
        recommendation_repository=recommendation_repository,
        context_repository=context_repository,
        prompt_builder=prompt_builder,
        analytics_api_url=settings.provided.analytics_service_url
    )
