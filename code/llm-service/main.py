# main.py
import asyncio
import logging
from src.infrastructure.config import Settings
from src.infrastructure.config.dependency_injection import Container
from src.presentation.api.app import create_app

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
    container.config.from_dict({
        'anthropic': {
            'api_key': settings.anthropic_api_key,
            'model': settings.model_name,
            'max_tokens': settings.max_tokens,
            'temperature': settings.temperature
        },
        'mongodb': {
            'uri': settings.mongo_uri,
            'database': settings.database_name
        },
        'app': settings.to_dict()
    })
    
    # Wire the container
    container.wire(modules=[
        'src.presentation.api.routes.analysis',
        'src.presentation.api.routes.chat',
        'src.presentation.api.routes.health'
    ])
    
    # Create FastAPI app
    app = create_app(container)
    
    # Run with uvicorn
    import uvicorn
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=5001,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())