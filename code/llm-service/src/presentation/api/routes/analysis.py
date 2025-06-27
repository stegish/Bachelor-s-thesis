from fastapi import APIRouter, Depends, UploadFile, File
from typing import List
from dependency_injector.wiring import inject, Provide
from ....infrastructure.config import Container
from ....application.use_cases import AnalyzeDataUseCase
from ....application.dto import AnalysisRequestDTO, AnalysisResponseDTO

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])

@router.post("/", response_model=AnalysisResponseDTO)
@inject
async def analyze(
    request: AnalysisRequestDTO,
    use_case: AnalyzeDataUseCase = Depends(Provide[Container.analyze_data_use_case])
):
    """Analyze data endpoint"""
    domain_request = request.to_domain()
    result = await use_case.execute(domain_request)
    return AnalysisResponseDTO.from_domain(result)

@router.post("/csv", response_model=AnalysisResponseDTO)
@inject
async def analyze_csv(
    question: str,
    files: List[UploadFile] = File(...),
    use_case: AnalyzeDataUseCase = Depends(Provide[Container.analyze_data_use_case])
):
    """Analyze CSV files"""
    # Process files and create request
    # Implementation here
    pass