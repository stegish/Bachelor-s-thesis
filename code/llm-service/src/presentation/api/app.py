from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging
from .routes import analytics, export, health, config
from .middleware import ErrorHandlerMiddleware, LoggingMiddleware
from ...infrastructure.config import Settings, Container
from ...application.dto import AnalyticsRequest

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting Manufacturing Analytics Service...")
    container = app.state.container
    settings = container.settings()
    
    # Initialize scheduler
    scheduler = container.scheduler()
    use_case = container.generate_analytics_use_case()
    
    # Define scheduled task
    async def scheduled_analytics():
        logger.info("Running scheduled analytics generation...")
        request = AnalyticsRequest(
            output_directory=settings.output_directory,
            grafana_directory=settings.grafana_csv_directory
        )
        result = await use_case.execute(request)
        logger.info(f"Scheduled analytics completed: {result.message}")
    
    # Schedule the task
    task_id = scheduler.schedule_task(
        scheduled_analytics,
        interval_minutes=settings.schedule_interval_minutes
    )
    logger.info(f"Analytics scheduled every {settings.schedule_interval_minutes} minutes")
    
    # Start scheduler
    scheduler.start()
    
    # Run initial analytics
    logger.info("Running initial analytics generation...")
    await scheduled_analytics()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Manufacturing Analytics Service...")
    scheduler.stop()
    logger.info("Scheduler stopped")

def create_app(container: Container) -> FastAPI:
    """Create and configure FastAPI application"""
    settings = container.settings()
    
    app = FastAPI(
        title="Manufacturing Analytics Service",
        version=settings.app_version,
        description="""
        Analytics service for manufacturing data with SOLID architecture.
        
        ## Features
        - Automated analytics generation
        - Real-time metrics calculation
        - CSV export for Grafana
        - Bottleneck identification
        - Operator performance tracking
        
        ## Architecture
        Built with Clean Architecture and SOLID principles for maintainability and extensibility.
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
    app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
    app.include_router(export.router, prefix="/export", tags=["export"])
    app.include_router(config.router, prefix="/config", tags=["configuration"])
    
    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        return {
            "service": "Manufacturing Analytics",
            "version": settings.app_version,
            "status": "operational",
            "environment": settings.environment,
            "endpoints": {
                "health": "/health",
                "docs": "/docs",
                "analytics": "/analytics",
                "export": "/export",
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
