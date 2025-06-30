import asyncio
import logging
from src.infrastructure.config import Settings
from src.infrastructure.config.dependency_injection import Container
from src.presentation.api.app import create_app
from dependency_injector import providers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Main entry point"""
    # Load settings
    settings = Settings()
    
    # Initialize container
    container = Container()
    
    # Use model_dump instead of to_dict for the config
    settings_dict = settings.model_dump()
    container.config.from_dict({
        'settings': settings_dict
    })
    
    # Override providers with actual instances
    container.settings.override(providers.Object(settings))
    
    # Wire the container
    container.wire(modules=[
        'src.presentation.api.routes.analysis',
        'src.presentation.api.routes.chat',
        'src.presentation.api.routes.health',
        'src.presentation.api.routes.mcp',
        'src.presentation.api.routes.suggestions',
        'src.presentation.api.routes.recommendations',
        'src.presentation.api.routes.config'
    ])
    
    # Create FastAPI app
    app = create_app(container)
    
    # Run with uvicorn
    import uvicorn
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=5001,
        log_level=settings.log_level.lower()
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())