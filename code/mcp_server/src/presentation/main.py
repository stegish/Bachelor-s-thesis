import asyncio
import logging
from code.mcp_server.mcp_server import ManufacturingMCPServer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Main entry point"""
    server = ManufacturingMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())