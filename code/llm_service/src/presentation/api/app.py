from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging
from .routes import analysis, chat, config, health, mcp, suggestions  # Added suggestions
from .middleware.error_handler import ErrorHandlerMiddleware
from .middleware.logging_middleware import LoggingMiddleware
from ...infrastructure.config import Settings, Container
from .routes import analysis, chat, config, health, mcp, suggestions, recommendations  # ADD recommendations


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting LLM Service...")
    yield
    # Shutdown
    logger.info("Shutting down LLM Service...")

def create_app(container: Container) -> FastAPI:
    """Create and configure FastAPI application"""
    settings = container.settings()
    
    app = FastAPI(
        title="Manufacturing LLM Service",
        version=settings.app_version,
        description="""
        AI-powered analytics service for manufacturing data using Claude.
        
        ## Features
        - CSV file analysis and comparison
        - Context-aware Q&A
        - Interactive chat with session management
        - MCP integration for data access
        - Real-time improvement suggestions
        """,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Store container in app state
    app.state.container = container
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add custom middleware
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(LoggingMiddleware)

    app.include_router(recommendations.router)  # ADD THIS LINE after the other routers

    
    # Add request timing middleware
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(analysis.router)
    app.include_router(chat.router)
    app.include_router(mcp.router)
    app.include_router(suggestions.router)  # Make sure this is included
    app.include_router(config.router, prefix="/config", tags=["configuration"])
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        return {
            "service": "Manufacturing LLM Service",
            "version": settings.app_version,
            "status": "operational",
            "environment": settings.environment,
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "analysis": "/api/v1/analysis",
                "chat": "/api/v1/chat",
                "mcp": "/api/v1/mcp",
                "suggestions": "/api/v1/suggestions",
                "recommendations": "/api/v1/recommendations",
                "config": "/config"
            }
        }
    
    # Custom exception handlers
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": str(exc),
                "type": "validation_error"
            }
        )
    
    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={
                "status": "error",
                "message": "Resource not found",
                "path": str(request.url)
            }
        )
    
    return app