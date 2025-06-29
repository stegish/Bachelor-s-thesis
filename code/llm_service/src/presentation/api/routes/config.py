from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from ....infrastructure.config import Container, Settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/settings")
@inject
async def get_current_settings(
    settings: Settings = Depends(Provide[Container.settings])
):
    """Get current service configuration (sanitized)"""
    # Sanitize sensitive data
    config = settings.to_dict()
    
    # Hide sensitive parts of connection strings
    if "mongo_uri" in config:
        if "@" in config["mongo_uri"]:
            parts = config["mongo_uri"].split("@")
            config["mongo_uri"] = f"{parts[0].split('//')[0]}//*****@{parts[1]}"
    
    return {
        "configuration": config,
        "service_info": {
            "name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment
        }
    }

@router.get("/capabilities")
async def get_service_capabilities():
    """Get service capabilities and features"""
    return {
        "analytics": {
            "phase_metrics": "Calculate detailed phase-level production metrics",
            "machine_metrics": "Track machine utilization and efficiency",
            "order_timeline": "Analyze order progress and delays",
            "bottleneck_detection": "Identify production bottlenecks",
            "operator_performance": "Measure operator efficiency"
        },
        "export_formats": ["CSV", "JSON", "ZIP"],
        "scheduling": {
            "supported": True,
            "configurable": True,
            "minimum_interval_minutes": 1
        },
        "api_features": {
            "async": True,
            "batch_processing": True,
            "real_time_queries": True,
            "file_download": True
        }
    }