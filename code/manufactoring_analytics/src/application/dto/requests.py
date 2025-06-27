# src/application/dto/requests.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class GenerateAnalyticsRequest(BaseModel):
    """Request DTO for generating analytics"""
    output_directory: str = Field(..., min_length=1)
    force_regenerate: bool = Field(default=False)
    
class ExportAnalyticsRequest(BaseModel):
    """Request DTO for exporting analytics"""
    format: str = Field(default='csv', pattern='^(csv|json|zip)$')
    include_summary: bool = Field(default=True)
    
class GetAnalyticsStatusRequest(BaseModel):
    """Request DTO for getting analytics status"""
    include_history: bool = Field(default=False)
    limit: Optional[int] = Field(default=10, ge=1, le=100)