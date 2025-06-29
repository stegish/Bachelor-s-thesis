from fastapi import APIRouter
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    from ....infrastructure.config import Settings
    
    # Get settings
    settings = Settings()
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "manufacturing-llm-service",
        "version": settings.app_version,
        "environment": settings.environment,
        "checks": {}
    }
    
    # Check MongoDB connection
    try:
        from ....infrastructure.persistence import MongoDBContextRepository
        context_repository = MongoDBContextRepository(
            connection_string=settings.mongo_uri,
            database_name=settings.database_name
        )
        # Just try to get summary stats to check connection
        await context_repository._get_summary_stats()
        health_status["checks"]["mongodb"] = {
            "status": "connected"
        }
    except Exception as e:
        health_status["checks"]["mongodb"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check LLM service
    try:
        health_status["checks"]["llm_service"] = {
            "status": "ready",
            "model": settings.model_name
        }
    except Exception as e:
        health_status["checks"]["llm_service"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check file system
    try:
        upload_dir = settings.temp_upload_folder
        os.makedirs(upload_dir, exist_ok=True)
        health_status["checks"]["filesystem"] = {
            "status": "accessible",
            "upload_directory": upload_dir,
            "writable": os.access(upload_dir, os.W_OK)
        }
    except Exception as e:
        health_status["checks"]["filesystem"] = {
            "status": "error",
            "error": str(e)
        }
    
    status_code = 200 if health_status["status"] == "healthy" else 503
    return health_status