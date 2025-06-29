import mcp.server.stdio
import mcp.types as types
from typing import Any
import logging
from ..infrastructure.config import get_settings
from ..infrastructure.persistence import MongoDBRepository
from ..infrastructure.external import AnalyticsAPIService
from ..application.use_cases import (
    QueryDatabaseUseCase,
    ReadCSVDataUseCase,
    GetProductionInsightsUseCase
)

logger = logging.getLogger(__name__)

class ManufacturingMCPServer:
    """MCP Server for manufacturing data access"""
    
    def __init__(self):
        self.settings = get_settings()
        self.name = self.settings.mcp_server_name
        self.version = self.settings.mcp_server_version
        
        # Initialize repositories
        self.mongo_repo = MongoDBRepository(
            self.settings.mongo_uri,
            self.settings.database_name
        )
        
        self.analytics_service = AnalyticsAPIService(
            self.settings.analytics_api_url
        )
        
        # Initialize use cases
        self.query_db_use_case = QueryDatabaseUseCase(self.mongo_repo)
        self.read_csv_use_case = ReadCSVDataUseCase(self.analytics_service)
        self.insights_use_case = GetProductionInsightsUseCase(
            self.mongo_repo,
            self.analytics_service
        )
        
        # Create MCP server
        self.server = mcp.server.stdio.create_server(self.name)
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register MCP protocol handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="query_database",
                    description="Query MongoDB collections for manufacturing data",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection": {
                                "type": "string",
                                "description": "Collection name (e.g., 'newOrdini', 'macchinari')"
                            },
                            "filter": {
                                "type": "object",
                                "description": "MongoDB query filter",
                                "default": {}
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of documents to return",
                                "default": 100
                            },
                            "projection": {
                                "type": "object",
                                "description": "Fields to include/exclude",
                                "default": {}
                            }
                        },
                        "required": ["collection"]
                    }
                ),
                types.Tool(
                    name="count_documents",
                    description="Count documents in a MongoDB collection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection": {
                                "type": "string",
                                "description": "Collection name"
                            },
                            "filter": {
                                "type": "object",
                                "description": "MongoDB query filter",
                                "default": {}
                            }
                        },
                        "required": ["collection"]
                    }
                ),
                types.Tool(
                    name="list_collections",
                    description="List all available MongoDB collections",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="get_collection_schema",
                    description="Get schema sample from a collection",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "collection": {
                                "type": "string",
                                "description": "Collection name"
                            }
                        },
                        "required": ["collection"]
                    }
                ),
                types.Tool(
                    name="list_csv_files",
                    description="List available CSV analytics files",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="read_csv_file",
                    description="Read content of a specific CSV file",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "CSV filename (e.g., 'machine_metrics.csv')"
                            }
                        },
                        "required": ["filename"]
                    }
                ),
                types.Tool(
                    name="get_all_csv_data",
                    description="Get all CSV analytics data in structured format",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="analyze_csv_file",
                    description="Analyze a CSV file and get statistical insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "filename": {
                                "type": "string",
                                "description": "CSV filename to analyze"
                            }
                        },
                        "required": ["filename"]
                    }
                ),
                types.Tool(
                    name="get_production_status",
                    description="Get current production status overview combining DB and CSV data",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Execute a tool"""
            logger.info(f"Executing tool: {name} with arguments: {arguments}")
            
            try:
                if name == "query_database":
                    result = await self.query_db_use_case.find_documents(
                        collection=arguments["collection"],
                        filter=arguments.get("filter", {}),
                        limit=arguments.get("limit", 100),
                        projection=arguments.get("projection", {})
                    )
                
                elif name == "count_documents":
                    result = await self.query_db_use_case.count_documents(
                        collection=arguments["collection"],
                        filter=arguments.get("filter", {})
                    )
                
                elif name == "list_collections":
                    result = await self.query_db_use_case.list_collections()
                
                elif name == "get_collection_schema":
                    result = await self.query_db_use_case.get_schema_sample(
                        collection=arguments["collection"]
                    )
                
                elif name == "list_csv_files":
                    result = await self.read_csv_use_case.list_csv_files()
                
                elif name == "read_csv_file":
                    result = await self.read_csv_use_case.read_csv_file(
                        filename=arguments["filename"]
                    )
                
                elif name == "get_all_csv_data":
                    result = await self.read_csv_use_case.get_all_csv_data()
                
                elif name == "analyze_csv_file":
                    result = await self.read_csv_use_case.analyze_csv_data(
                        filename=arguments["filename"]
                    )
                
                elif name == "get_production_status":
                    result = await self.insights_use_case.get_current_status()
                
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
                
                # Convert result to MCP format
                mcp_result = result.to_mcp_format()
                
                # Extract text content
                content = mcp_result.get("content", [])
                if content and isinstance(content[0], dict):
                    return [types.TextContent(
                        type="text",
                        text=content[0].get("text", "No result")
                    )]
                
                return [types.TextContent(
                    type="text",
                    text="No result returned"
                )]
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return [types.TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
    
    async def run(self):
        """Run the MCP server"""
        logger.info(f"Starting {self.name} v{self.version}")
        await self.server.run()