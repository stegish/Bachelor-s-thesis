# src/application/dto/responses.py
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

class AnalyticsResponse(BaseModel):
    """Response DTO for analytics operations"""
    status: str
    message: str
    timestamp: datetime
    data: Optional[Dict[str, Any]] = None
    
class GenerateAnalyticsResponse(AnalyticsResponse):
    """Response DTO for generate analytics"""
    files_generated: int
    summary: Dict[str, Any]
    
class ExportAnalyticsResponse(AnalyticsResponse):
    """Response DTO for export analytics"""
    file_path: str
    file_size: int
    format: str
    
class AnalyticsStatusResponse(AnalyticsResponse):
    """Response DTO for analytics status"""
    last_run: Optional[datetime]
    next_scheduled_run: Optional[datetime]
    is_running: bool
    files_available: List[str]
    history: Optional[List[Dict[str, Any]]] = None