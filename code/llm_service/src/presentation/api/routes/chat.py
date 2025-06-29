from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dependency_injector.wiring import inject, Provide
from ....infrastructure.config import Container
from ....application.use_cases import ChatUseCase
from ....application.dto import ChatResponseDTO
from datetime import datetime

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str
    session_id: str

@router.post("/", response_model=ChatResponseDTO)
@inject
async def chat(
    request: ChatRequest,
    use_case: ChatUseCase = Depends(Provide[Container.chat_use_case])
):
    """Chat endpoint"""
    try:
        response = await use_case.execute(request.message, request.session_id)
        
        return ChatResponseDTO(
            message=response,
            session_id=request.session_id,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
