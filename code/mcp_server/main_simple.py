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

class ScheduleOrderRequest(BaseModel):
    order: Dict[str, Any]

class AddMachineStaffRequest(BaseModel):
    machine_id: str
    staff: List[str]

class RescheduleOrdersRequest(BaseModel):
    machine_id: str
    schedule: Dict[str, Any]

class UpdateOrderRequest(BaseModel):
    order_id: str
    updates: Dict[str, Any]

class UpdatePhaseRequest(BaseModel):
    order_id: str
    phase_id: str
    updates: Dict[str, Any]

class AddOrderNoteRequest(BaseModel):
    order_id: str
    note: Dict[str, Any]

class UpdateMachineRequest(BaseModel):
    machine_id: str
    updates: Dict[str, Any]

class UpdateShiftRequest(BaseModel):
    shift_id: str
    updates: Dict[str, Any]

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
            },
            {
                "name": "schedule_order",
                "description": "Insert a new order into the production plan"
            },
            {
                "name": "add_machine_staff",
                "description": "Assign additional operators to a machine"
            },
            {
                "name": "reschedule_machine_orders",
                "description": "Reschedule all orders for a machine"
            },
            {
                "name": "get_working_hours",
                "description": "Return company working hours information"
            },
            {
                "name": "update_order",
                "description": "Update fields of an order"
            },
            {
                "name": "update_phase",
                "description": "Update fields of a phase inside an order"
            },
            {
                "name": "add_order_note",
                "description": "Append a note to an order"
            },
            {
                "name": "update_machine",
                "description": "Modify machine settings like queueTargetTime or activation"
            },
            {
                "name": "update_shift",
                "description": "Modify or add overtime to a shift"
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


@app.post("/tools/schedule_order")
async def schedule_order(request: ScheduleOrderRequest):
    """Insert a new production order"""
    try:
        order_id = await mongo_repo.insert_order(request.order)
        return {"success": True, "order_id": order_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/add_machine_staff")
async def add_machine_staff(request: AddMachineStaffRequest):
    """Assign additional staff to a machine"""
    try:
        modified = await mongo_repo.add_machine_staff(request.machine_id, request.staff)
        return {"success": True, "modified": modified}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/reschedule_machine_orders")
async def reschedule_machine_orders(request: RescheduleOrdersRequest):
    """Reschedule orders for a machine"""
    try:
        modified = await mongo_repo.reschedule_machine_orders(request.machine_id, request.schedule)
        return {"success": True, "modified": modified}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tools/get_working_hours")
async def get_working_hours():
    """Return company working hours"""
    try:
        data = await mongo_repo.get_working_hours()
        return {"success": True, "data": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/update_order")
async def update_order(request: UpdateOrderRequest):
    """Update fields of an order"""
    try:
        modified = await mongo_repo.update_order_fields(request.order_id, request.updates)
        return {"success": True, "modified": modified}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/update_phase")
async def update_phase(request: UpdatePhaseRequest):
    """Update a specific phase inside an order"""
    try:
        modified = await mongo_repo.update_phase_fields(request.order_id, request.phase_id, request.updates)
        return {"success": True, "modified": modified}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/add_order_note")
async def add_order_note(request: AddOrderNoteRequest):
    """Append a note to an order"""
    try:
        modified = await mongo_repo.add_order_note(request.order_id, request.note)
        return {"success": True, "modified": modified}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/update_machine")
async def update_machine(request: UpdateMachineRequest):
    """Update machine settings"""
    try:
        modified = await mongo_repo.update_machine(request.machine_id, request.updates)
        return {"success": True, "modified": modified}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/tools/update_shift")
async def update_shift(request: UpdateShiftRequest):
    """Update shift information or overtime"""
    try:
        modified = await mongo_repo.update_shift(request.shift_id, request.updates)
        return {"success": True, "modified": modified}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002, log_level="info")