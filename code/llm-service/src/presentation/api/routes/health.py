from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from ....infrastructure.config import Container
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
@inject
async def health_check(
    container: Container = Depends(Provide[Container])
):
    """Comprehensive health check endpoint"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "manufacturing-analytics",
        "version": container.settings().app_version,
        "environment": container.settings().environment,
        "checks": {}
    }
    
    # Check MongoDB connection
    try:
        data_repository = container.data_repository()
        latest_run = await data_repository.get_latest_analytics_run()
        health_status["checks"]["mongodb"] = {
            "status": "connected",
            "latest_analytics_run": latest_run.get("timestamp") if latest_run else None
        }
    except Exception as e:
        health_status["checks"]["mongodb"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check scheduler
    try:
        scheduler = container.scheduler()
        health_status["checks"]["scheduler"] = {
            "status": "running" if scheduler.is_running() else "stopped",
            "tasks": len(scheduler.get_scheduled_tasks())
        }
    except Exception as e:
        health_status["checks"]["scheduler"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check file system
    try:
        import os
        output_dir = container.settings().output_directory
        health_status["checks"]["filesystem"] = {
            "status": "accessible",
            "output_directory": output_dir,
            "writable": os.access(output_dir, os.W_OK) if os.path.exists(output_dir) else False
        }
    except Exception as e:
        health_status["checks"]["filesystem"] = {
            "status": "error",
            "error": str(e)
        }
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return health_status
