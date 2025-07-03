from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from .routes.csv_export import router as csv_router
from motor.motor_asyncio import AsyncIOMotorClient
from dependency_injector import providers
from .routes.health import router as health_router
from .routes.analytics import router as analytics_router
from .routes.export import router as export_router
from .routes.config import router as config_router
from ...infrastructure.config import Container, get_settings
from ...infrastructure.persistence.mongodb.repositories import OrderRepository, MachineRepository, AnalyticsRepository

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize DI container
container = Container()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application lifecycle"""
    # Startup
    logger.info("Starting Manufacturing Analytics API...")
    
    # Get settings instance
    settings = get_settings()
    
    # Initialize MongoDB connection with actual string values
    mongo_client = AsyncIOMotorClient(settings.mongo_uri)
    container.mongo_client.override(providers.Object(mongo_client))
    
    # Override repositories with proper database names
    container.order_repository.override(
        providers.Singleton(
            OrderRepository,
            client=mongo_client,
            database_name=settings.database_name
        )
    )
    
    container.machine_repository.override(
        providers.Singleton(
            MachineRepository,
            client=mongo_client,
            database_name=settings.get_process_db_name()
        )
    )
    
    container.analytics_repository.override(
        providers.Singleton(
            AnalyticsRepository,
            client=mongo_client,
            database_name=settings.database_name
        )
    )
    
    # Wire the container
    container.wire(modules=[
        "src.presentation.api.routes.health",
        "src.presentation.api.routes.analytics", 
        "src.presentation.api.routes.export",
        "src.presentation.api.routes.config",
        "src.presentation.api.routes.csv_export"
    ])
    
    # Initialize scheduler
    scheduler = container.scheduler_service()
    scheduler.start()  # Start scheduler before adding jobs
    
    use_case = container.generate_analytics_use_case()
    
    # Schedule analytics generation
    async def scheduled_analytics():
        logger.info("Running scheduled analytics...")
        try:
            await use_case.execute(settings.output_directory)
        except Exception as e:
            logger.error(f"Error running scheduled analytics: {e}")
    
    scheduler.schedule_task(scheduled_analytics, settings.schedule_interval_minutes)
    
    # Run initial analytics
    try:
        await scheduled_analytics()
    except Exception as e:
        logger.error(f"Error running initial analytics: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Manufacturing Analytics API...")
    scheduler.stop()
    mongo_client.close()

# Create FastAPI app
app = FastAPI(
    title="Manufacturing Analytics API",
    description="Hexagonal Architecture Manufacturing Analytics System",
    version="2.0.0",
    lifespan=lifespan
)

# Add middleware
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"{request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
    )
    
    # Add process time header
    response.headers["X-Process-Time"] = str(process_time)
    
    return response

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include routers
app.include_router(health_router)
app.include_router(csv_router, prefix=settings.api_prefix)
app.include_router(analytics_router, prefix=settings.api_prefix)
app.include_router(export_router, prefix=settings.api_prefix)
app.include_router(config_router, prefix=settings.api_prefix)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Manufacturing Analytics API",
        "version": "2.0.0",
        "description": "Hexagonal Architecture Manufacturing Analytics System",
        "docs": "/docs",
        "health": "/health",
        "api": {
            "analytics": f"{settings.api_prefix}/analytics",
            "export": f"{settings.api_prefix}/export",
            "config": f"{settings.api_prefix}/config"
        }
    }