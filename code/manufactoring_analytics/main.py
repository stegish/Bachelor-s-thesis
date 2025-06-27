import uvicorn
from src.presentation.api.main import app
from src.infrastructure.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    
    uvicorn.run(
        "src.presentation.api.main:app",
        host="0.0.0.0",
        port=5000,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )