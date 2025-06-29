# src/application/use_cases/process_csv.py
from typing import List, Dict, Any
import pandas as pd
from ...domain.interfaces import ILLMService
from ...domain.entities import AnalysisRequest, AnalysisResult
from ...domain.value_objects import FileData
from ..services import PromptBuilder

class ProcessCSVUseCase:
    """Use case for CSV file processing and analysis"""
    
    def __init__(
        self, 
        llm_service: ILLMService,
        prompt_builder: PromptBuilder
    ):
        self.llm_service = llm_service
        self.prompt_builder = prompt_builder
    
    async def execute(
        self, 
        files: List[FileData], 
        question: str
    ) -> AnalysisResult:
        """Process CSV files and analyze with LLM"""
        # Process each CSV file
        processed_data = {}
        
        for file_data in files:
            df = pd.read_csv(pd.io.common.BytesIO(file_data.content))
            
            # Calculate statistics
            stats = {
                'row_count': len(df),
                'columns': df.columns.tolist(),
                'numeric_summary': df.describe().to_dict() if not df.select_dtypes(include=['number']).empty else {},
                'missing_values': df.isnull().sum().to_dict()
            }
            
            processed_data[file_data.filename] = {
                'statistics': stats,
                'dataframe': df,
                'sample': df.head(10).to_dict('records')
            }
        
        # Create analysis request
        request = AnalysisRequest(
            question=question,
            context_data=processed_data,
            include_db_context=False
        )
        
        # Build prompt and analyze
        optimized_request = self.prompt_builder.build(request)
        result = await self.llm_service.analyze(optimized_request)
        
        # Add file information
        result.files_processed = [f.filename for f in files]
        
        return result