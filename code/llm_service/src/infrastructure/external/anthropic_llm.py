import asyncio
from typing import Dict, Any, Optional
from anthropic import AsyncAnthropic
from ...domain.interfaces import ILLMService
from ...domain.entities import AnalysisRequest, AnalysisResult
from ..config.settings import Settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AnthropicLLMService(ILLMService):
    """Anthropic implementation of LLM service"""
    
    def __init__(self, settings: Settings):
        self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.model = settings.model_name
        self.max_tokens = settings.max_tokens
        self.temperature = settings.temperature
        self.chat_sessions = {}  # In-memory chat storage
        
    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Implement analysis using Anthropic API"""
        start_time = datetime.now()
        
        # Build context from request
        context = self._build_context(request)
        
        # Create messages
        messages = [
            {
                "role": "system",
                "content": self._get_system_prompt()
            },
            {
                "role": "user",
                "content": f"{context}\n\nQuestion: {request.question}"
            }
        ]
        
        try:
            # Call Anthropic API
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=messages
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AnalysisResult(
                question=request.question,
                answer=response.content[0].text,
                model_used=self.model,
                context_included=request.include_db_context,
                session_id=request.session_id,
                timestamp=datetime.now(),
                data_provided=bool(request.context_data),
                files_processed=request.files and [f.filename for f in request.files],
                token_count=response.usage.total_tokens if hasattr(response, 'usage') else None,
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Error calling Anthropic API: {str(e)}")
            raise
    
    async def chat(self, message: str, session_id: str) -> str:
        """Chat with maintained context"""
        # Get or create session
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = []
        
        # Add user message to history
        self.chat_sessions[session_id].append({"role": "user", "content": message})
        
        # Build messages including history
        messages = [
            {"role": "system", "content": self._get_system_prompt()}
        ] + self.chat_sessions[session_id]
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=messages
            )
            
            # Add assistant response to history
            assistant_response = response.content[0].text
            self.chat_sessions[session_id].append({
                "role": "assistant",
                "content": assistant_response
            })
            
            # Limit history to last 20 messages
            if len(self.chat_sessions[session_id]) > 20:
                self.chat_sessions[session_id] = self.chat_sessions[session_id][-20:]
            
            return assistant_response
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            raise
    
    def _build_context(self, request: AnalysisRequest) -> str:
        """Build context from request data"""
        context_parts = []
        
        if request.context_data:
            # System prompt is handled separately
            if 'system_prompt' in request.context_data:
                return request.context_data.get('formatted_context', '')
            
            # Build context from data
            for key, value in request.context_data.items():
                if key != 'formatted_context':
                    context_parts.append(f"{key}:\n{value}")
        
        return '\n\n'.join(context_parts)
    
    def _get_system_prompt(self) -> str:
        """Get manufacturing-specific system prompt"""
        return """You are an AI assistant specialized in manufacturing analytics and production optimization. 
        You have deep expertise in:
        - Production planning and scheduling
        - Machine utilization and OEE (Overall Equipment Effectiveness)
        - Quality control and defect analysis
        - Supply chain optimization
        - Lean manufacturing principles
        - Industry 4.0 technologies
        
        When analyzing manufacturing data:
        1. Provide specific, actionable insights
        2. Identify patterns, anomalies, and trends
        3. Suggest concrete optimizations with expected impact
        4. Use relevant KPIs and metrics
        5. Consider costs, lead times, and efficiency
        6. Recommend preventive actions
        
        Always be precise with numbers, percentages, and calculations. Explain your reasoning clearly."""
