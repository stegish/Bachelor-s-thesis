from fastapi import APIRouter, Depends
from typing import Dict, Any
from ....infrastructure.config import get_settings, Settings
from dependency_injector.wiring import inject, Provide

router = APIRouter(prefix="/config", tags=["config"])

@router.get("/settings")
async def get_settings_info(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    """Get current service configuration"""
    return {
        'mongo_uri': settings.mongo_uri.replace(
            settings.mongo_uri.split('@')[0].split('//')[-1], 
            '***'
        ) if '@' in settings.mongo_uri else settings.mongo_uri,
        'database_name': settings.database_name,
        'process_database_name': settings.process_db_name,
        'output_directory': settings.output_directory,
        'schedule_interval_minutes': settings.schedule_interval_minutes,
        'service_info': {
            'name': settings.app_name,
            'version': settings.app_version,
            'environment': settings.environment
        }
    }

@router.get("/capabilities")
async def get_capabilities() -> Dict[str, Any]:
    """Get service capabilities"""
    return {
        'analytics': {
            'phase_metrics': 'Calculate detailed phase-level production metrics',
            'machine_metrics': 'Track machine utilization and efficiency',
            'order_timeline': 'Analyze order progress and delays',
            'bottleneck_detection': 'Identify production bottlenecks',
            'operator_performance': 'Measure operator efficiency'
        },
        'export_formats': ['CSV', 'JSON', 'ZIP'],
        'scheduling': {
            'supported': True,
            'configurable': True,
            'minimum_interval_minutes': 1
        },
        'api_features': {
            'async': True,
            'batch_processing': True,
            'real_time_queries': True,
            'file_download': True
        },
        'architecture': {
            'style': 'Hexagonal Architecture',
            'principles': ['SOLID', 'Clean Architecture', 'DDD'],
            'layers': ['Domain', 'Application', 'Infrastructure', 'Presentation']
        }
    }