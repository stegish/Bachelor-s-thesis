from typing import Dict, Any
from ...domain.entities import AnalysisRequest

class ContextEnricher:
    """Service to enrich analysis requests with database context"""
    
    def enrich(self, request: AnalysisRequest, db_context: Dict[str, Any]) -> AnalysisRequest:
        """Enrich request with database context"""
        if request.context_data is None:
            request.context_data = {}
        
        # Merge database context with existing context
        request.context_data.update({
            'database_context': db_context,
            'context_enriched': True
        })
        
        return request