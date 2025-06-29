from typing import Dict, Any
from ...domain.interfaces import ILLMService, IContextRepository
from ...domain.entities import AnalysisRequest, AnalysisResult
from ..services import PromptBuilder, ContextEnricher

class AnalyzeDataUseCase:
    """Use case for data analysis following Single Responsibility Principle"""
    
    def __init__(
        self,
        llm_service: ILLMService,
        context_repository: IContextRepository,
        prompt_builder: PromptBuilder,
        context_enricher: ContextEnricher
    ):
        self.llm_service = llm_service
        self.context_repository = context_repository
        self.prompt_builder = prompt_builder
        self.context_enricher = context_enricher
        
    async def execute(self, request: AnalysisRequest) -> AnalysisResult:
        """Execute analysis use case"""
        # 1. Enrich context if needed
        if request.include_db_context:
            db_context = await self.context_repository.get_context(request.question)
            request = self.context_enricher.enrich(request, db_context)
        
        # 2. Build optimized prompt
        optimized_request = self.prompt_builder.build(request)
        
        # 3. Call LLM service
        result = await self.llm_service.analyze(optimized_request)
        
        # 4. Save to history
        await self.context_repository.save_history(request, result)
        
        return result