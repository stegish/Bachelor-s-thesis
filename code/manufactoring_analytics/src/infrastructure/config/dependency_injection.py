from dependency_injector import containers, providers
from motor.motor_asyncio import AsyncIOMotorClient
from .settings import Settings, get_settings
from ..persistence.mongodb.repositories import OrderRepository, MachineRepository, AnalyticsRepository
from ..persistence.file_system.csv_exporter import CSVExporter
from ..external.scheduler import Scheduler
from ...application.services import PhaseAnalyzer, MachineAnalyzer, OrderAnalyzer, BottleneckDetector
from ...application.use_cases import GenerateAnalyticsUseCase, ExportAnalyticsUseCase, GetAnalyticsStatusUseCase

class Container(containers.DeclarativeContainer):
    # Configuration
    config = providers.Configuration()
    
    # Settings instance
    settings = providers.Singleton(get_settings)
    
    # MongoDB Connection - using a factory to properly pass the URI
    mongo_client = providers.Singleton(
        AsyncIOMotorClient,
        settings.provided.mongo_uri
    )
    
    # Repositories
    order_repository = providers.Singleton(
        OrderRepository,
        client=mongo_client,
        database_name=settings.provided.database_name
    )
    
    machine_repository = providers.Singleton(
        MachineRepository,
        client=mongo_client,
        database_name=settings.provided.process_db_name
    )
    
    analytics_repository = providers.Singleton(
        AnalyticsRepository,
        client=mongo_client,
        database_name=settings.provided.database_name
    )
    
    # Services
    export_service = providers.Singleton(CSVExporter)
    scheduler_service = providers.Singleton(Scheduler)
    
    # Application Services
    phase_analyzer = providers.Singleton(PhaseAnalyzer)
    machine_analyzer = providers.Singleton(MachineAnalyzer)
    order_analyzer = providers.Singleton(OrderAnalyzer)
    bottleneck_detector = providers.Singleton(BottleneckDetector)
    
    # Use Cases
    generate_analytics_use_case = providers.Factory(
        GenerateAnalyticsUseCase,
        order_repository=order_repository,
        machine_repository=machine_repository,
        export_service=export_service,
        phase_analyzer=phase_analyzer,
        machine_analyzer=machine_analyzer,
        order_analyzer=order_analyzer,
        bottleneck_detector=bottleneck_detector
    )
    
    export_analytics_use_case = providers.Factory(
        ExportAnalyticsUseCase,
        analytics_repository=analytics_repository,
        output_directory=settings.provided.output_directory
    )
    
    get_analytics_status_use_case = providers.Factory(
        GetAnalyticsStatusUseCase,
        analytics_repository=analytics_repository,
        scheduler_service=scheduler_service,
        output_directory=settings.provided.output_directory
    )