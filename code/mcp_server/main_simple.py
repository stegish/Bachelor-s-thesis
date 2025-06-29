#!/usr/bin/env python3
"""
Simplified MCP Server implementation for manufacturing data access.
This version provides a REST API interface instead of stdio protocol
for easier integration and testing.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import logging
from src.infrastructure.config import get_settings
from src.infrastructure.persistence import MongoDBRepository
from src.infrastructure.external import AnalyticsAPIService
from src.application.use_cases import (
    QueryDatabaseUseCase,
    ReadCSVDataUseCase,
    GetProductionInsightsUseCase
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Manufacturing MCP Server",
    description="MCP-compatible server for manufacturing data access",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
settings = get_settings()
mongo_repo = MongoDBRepository(settings.mongo_uri, settings.database_name)
analytics_service = AnalyticsAPIService(settings.analytics_api_url)

# Initialize use cases
query_db_use_case = QueryDatabaseUseCase(mongo_repo)
read_csv_use_case = ReadCSVDataUseCase(analytics_service)
insights_use_case = GetProductionInsightsUseCase(mongo_repo, analytics_service)

# Request models
class QueryDatabaseRequest(BaseModel):
    collection: str
    filter: Optional[Dict[str, Any]] = {}
    limit: Optional[int] = 100
    projection: Optional[Dict[str, Any]] = {}

class CountDocumentsRequest(BaseModel):
    collection: str
    filter: Optional[Dict[str, Any]] = {}

# API Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "manufacturing-mcp"}

@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": "query_database",
                "description": "Query MongoDB collections for manufacturing data"
            },
            {
                "name": "count_documents",
                "description": "Count documents in a MongoDB collection"
            },
            {
                "name": "list_collections",
                "description": "List all available MongoDB collections"
            },
            {
                "name": "get_collection_schema",
                "description": "Get schema sample from a collection"
            },
            {
                "name": "list_csv_files",
                "description": "List available CSV analytics files"
            },
            {
                "name": "read_csv_file",
                "description": "Read content of a specific CSV file"
            },
            {
                "name": "get_all_csv_data",
                "description": "Get all CSV analytics data in structured format"
            },
            {
                "name": "get_production_status",
                "description": "Get current production status overview"
            }
        ]
    }

@app.post("/tools/query_database")
async def query_database(request: QueryDatabaseRequest):
    """Query MongoDB collection"""
    result = await query_db_use_case.find_documents(
        collection=request.collection,
        filter=request.filter,
        limit=request.limit,
        projection=request.projection
    )
    
    if result.success:
        return {"success": True, "data": result.data, "metadata": result.metadata}
    else:
        raise HTTPException(status_code=400, detail=result.error)

@app.post("/tools/count_documents")
async def count_documents(request: CountDocumentsRequest):
    """Count documents in collection"""
    result = await query_db_use_case.count_documents(
        collection=request.collection,
        filter=request.filter
    )
    
    if result.success:
        return {"success": True, "count": result.data}
    else:
        raise HTTPException(status_code=400, detail=result.error)

@app.get("/tools/list_collections")
async def list_collections():
    """List all collections"""
    result = await query_db_use_case.list_collections()
    
    if result.success:
        return {"success": True, "collections": result.data}
    else:
        raise HTTPException(status_code=400, detail=result.error)

@app.get("/tools/get_collection_schema/{collection}")
async def get_collection_schema(collection: str):
    """Get collection schema"""
    result = await query_db_use_case.get_schema_sample(collection)
    
    if result.success:
        return {"success": True, "schema": result.data}
    else:
        raise HTTPException(status_code=400, detail=result.error)

@app.get("/tools/list_csv_files")
async def list_csv_files():
    """List CSV files"""
    result = await read_csv_use_case.list_csv_files()
    
    if result.success:
        return {"success": True, "files": result.data}
    else:
        raise HTTPException(status_code=400, detail=result.error)

@app.get("/tools/read_csv_file/{filename}")
async def read_csv_file(filename: str):
    """Read CSV file"""
    result = await read_csv_use_case.read_csv_file(filename)
    
    if result.success:
        return {"success": True, "data": result.data, "metadata": result.metadata}
    else:
        raise HTTPException(status_code=400, detail=result.error)

@app.get("/tools/get_all_csv_data")
async def get_all_csv_data():
    """Get all CSV data"""
    result = await read_csv_use_case.get_all_csv_data()
    
    if result.success:
        return {"success": True, "data": result.data, "metadata": result.metadata}
    else:
        raise HTTPException(status_code=400, detail=result.error)

@app.get("/tools/get_production_status")
async def get_production_status():
    """Get production status"""
    result = await insights_use_case.get_current_status()
    
    if result.success:
        return {"success": True, "status": result.data}
    else:
        raise HTTPException(status_code=400, detail=result.error)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002, log_level="info")