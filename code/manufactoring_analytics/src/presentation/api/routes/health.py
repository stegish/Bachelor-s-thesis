from fastapi import APIRouter, Depends
from typing import Dict, Any
from datetime import datetime
from ....infrastructure.config import get_settings, Settings
import platform
import psutil

router = APIRouter(tags=["health"])

@router.get("/health")
async def health_check(settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    """Health check endpoint with system information"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "system": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
    }

@router.get("/ready")
async def readiness_check() -> Dict[str, str]:
    """Readiness check for Kubernetes"""
    # In a real implementation, check database connectivity, etc.
    return {"status": "ready"}

@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """Liveness check for Kubernetes"""
    return {"status": "alive"}