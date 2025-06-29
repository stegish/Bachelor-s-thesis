from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import List, Optional
from dependency_injector.wiring import inject, Provide
from ....infrastructure.config import Container
from ....application.use_cases import AnalyzeDataUseCase, ProcessCSVUseCase
from ....application.dto import AnalysisRequestDTO, AnalysisResponseDTO
from ....domain.value_objects import FileData
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

@router.post("/", response_model=AnalysisResponseDTO)
@inject
async def analyze(
    request: AnalysisRequestDTO,
    use_case: AnalyzeDataUseCase = Depends(Provide[Container.analyze_data_use_case])
):
    """Analyze data endpoint"""
    try:
        domain_request = request.to_domain()
        result = await use_case.execute(domain_request)
        return AnalysisResponseDTO.from_domain(result)
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/csv", response_model=AnalysisResponseDTO)
@inject
async def analyze_csv(
    question: str = Form(...),
    include_context: bool = Form(True),
    files: List[UploadFile] = File(...),
    use_case: ProcessCSVUseCase = Depends(Provide[Container.process_csv_use_case])
):
    """Analyze CSV files"""
    try:
        # Validate files
        file_data_list = []
        for file in files:
            if not file.filename.endswith('.csv'):
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} is not a CSV file"
                )
            
            content = await file.read()
            file_data = FileData(
                filename=file.filename,
                content=content,
                content_type=file.content_type,
                size=len(content)
            )
            file_data_list.append(file_data)
        
        # Process CSV files
        result = await use_case.execute(file_data_list, question)
        
        return AnalysisResponseDTO.from_domain(result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"CSV analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/csv/compare", response_model=AnalysisResponseDTO)
@inject
async def compare_csv(
    question: Optional[str] = Form(None),
    files: List[UploadFile] = File(...),
    use_case: ProcessCSVUseCase = Depends(Provide[Container.process_csv_use_case])
):
    """Compare multiple CSV files"""
    if len(files) < 2:
        raise HTTPException(
            status_code=400,
            detail="At least 2 CSV files required for comparison"
        )
    
    # Auto-generate question if not provided
    if not question:
        filenames = [f.filename for f in files]
        question = f"Compare the following CSV files and identify key differences, trends, and patterns: {', '.join(filenames)}"
    
    return await analyze_csv(question=question, include_context=False, files=files, use_case=use_case)
