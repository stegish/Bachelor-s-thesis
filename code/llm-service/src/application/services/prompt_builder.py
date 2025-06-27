# src/application/services/prompt_builder.py
from typing import Dict, Any, List
from ...domain.entities import AnalysisRequest
import pandas as pd

class PromptBuilder:
    """Service to build optimized prompts following SRP"""
    
    MANUFACTURING_PROMPT = """You are an AI assistant specialized in manufacturing analytics and production optimization. 
    You have access to real-time manufacturing data including:
    - Production orders and their status
    - Machine utilization and efficiency metrics
    - Phase-level production data
    - Operator performance metrics
    - Queue analysis and bottleneck identification
    
    When analyzing data:
    1. Provide specific, actionable insights
    2. Identify patterns and anomalies
    3. Suggest optimizations based on the data
    4. Use metrics and KPIs relevant to manufacturing
    5. Consider lead times, delays, and efficiency when making recommendations
    
    Always be precise with numbers and percentages, and explain your reasoning."""
    
    def build(self, request: AnalysisRequest) -> AnalysisRequest:
        """Build optimized prompt with context"""
        context_parts = []
        
        # Add database context if available
        if request.context_data:
            context_parts.append(self._format_context(request.context_data))
        
        # Update request with formatted context
        request.context_data = {
            'formatted_context': '\n'.join(context_parts),
            'system_prompt': self.MANUFACTURING_PROMPT
        }
        
        return request
    
    def _format_context(self, data: Dict[str, Any]) -> str:
        """Format context data for LLM consumption"""
        formatted_parts = []
        
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                # Limit DataFrame rows
                display_rows = min(len(value), 100)
                formatted_parts.append(
                    f"\n{key} (showing {display_rows} of {len(value)} rows):\n"
                    f"{value.head(display_rows).to_string()}"
                )
            elif isinstance(value, list) and len(value) > 0:
                if isinstance(value[0], dict):
                    df = pd.DataFrame(value)
                    display_rows = min(len(df), 100)
                    formatted_parts.append(
                        f"\n{key} (showing {display_rows} of {len(df)} rows):\n"
                        f"{df.head(display_rows).to_string()}"
                    )
                else:
                    formatted_parts.append(f"\n{key}: {value[:100]}")
            else:
                formatted_parts.append(f"\n{key}: {value}")
        
        return '\n'.join(formatted_parts)