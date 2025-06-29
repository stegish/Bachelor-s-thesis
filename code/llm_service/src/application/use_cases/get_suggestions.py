from typing import Dict, Any, List
from ...domain.interfaces import ILLMService
from ...domain.entities import AnalysisRequest, AnalysisResult

class GetSuggestionsUseCase:
    """Use case for getting improvement suggestions"""
    
    def __init__(self, llm_service: ILLMService):
        self.llm_service = llm_service
    
    async def execute(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate suggestions based on metrics"""
        # Create a specific prompt for suggestions
        prompt = self._build_suggestions_prompt(metrics)
        
        request = AnalysisRequest(
            question=prompt,
            context_data={'metrics': metrics},
            include_db_context=False
        )
        
        result = await self.llm_service.analyze(request)
        
        # Parse suggestions from the response
        suggestions = self._parse_suggestions(result.answer)
        
        return suggestions
    
    def _build_suggestions_prompt(self, metrics: Dict[str, Any]) -> str:
        """Build prompt for suggestions"""
        return f"""Based on these manufacturing metrics:
        {metrics}
        
        Please provide specific, actionable recommendations to improve:
        1. Machine utilization
        2. On-time delivery rate
        3. Bottleneck resolution
        
        Format each suggestion as a numbered list item."""
    
    def _parse_suggestions(self, answer: str) -> List[str]:
        """Parse suggestions from LLM response"""
        lines = answer.strip().split('\n')
        suggestions = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering/bullets
                suggestion = line.lstrip('0123456789.-) ').strip()
                if suggestion:
                    suggestions.append(suggestion)
        
        return suggestions