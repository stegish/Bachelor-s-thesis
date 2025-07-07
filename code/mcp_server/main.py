# File: mcp_server/main_simple.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "AI-manager")
AI_MANAGER_DB_URI = os.getenv("AI_MANAGER_DB_URI", MONGO_URI)
AI_MANAGER_DB_NAME = os.getenv("AI_MANAGER_DB_NAME", "AI-manager")
PORT = int(os.getenv("PORT", "5002"))

# Initialize FastAPI app
app = FastAPI(
    title="Manufacturing MCP Server",
    description="Model Context Protocol server for manufacturing operations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB client
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]
ai_manager_client = AsyncIOMotorClient(AI_MANAGER_DB_URI)
ai_manager_db = ai_manager_client[AI_MANAGER_DB_NAME]

# Request/Response Models
class QueryDatabaseRequest(BaseModel):
    collection: str
    filter: Dict[str, Any] = {}
    limit: int = 100
    projection: Optional[Dict[str, Any]] = None

class CountDocumentsRequest(BaseModel):
    collection: str
    filter: Dict[str, Any] = {}

class UpdateOrderRequest(BaseModel):
    order_id: str
    updates: Dict[str, Any]

class UpdateOrderPriorityRequest(BaseModel):
    order_id: str
    priority: int

class UpdateMachineRequest(BaseModel):
    machine_id: str
    updates: Dict[str, Any]

class AddOrderNoteRequest(BaseModel):
    order_id: str
    note: str

class AddMachineStaffRequest(BaseModel):
    machine_id: str
    staff: List[str]

class RescheduleOrdersRequest(BaseModel):
    machine_id: str
    schedule: Dict[str, Any]

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        await db.command("ping")
        return {"status": "healthy", "service": "manufacturing-mcp", "mongodb": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "service": "manufacturing-mcp", "error": str(e)}

# Tools list
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
                "name": "update_order",
                "description": "Update fields of an order"
            },
            {
                "name": "update_order_priority",
                "description": "Update order priority"
            },
            {
                "name": "update_machine",
                "description": "Modify machine settings"
            },
            {
                "name": "add_order_note",
                "description": "Append a note to an order"
            },
            {
                "name": "add_machine_staff",
                "description": "Assign additional operators to a machine"
            },
            {
                "name": "reschedule_machine_orders",
                "description": "Reschedule all orders for a machine"
            }
        ]
    }

# Query operations
@app.post("/tools/query_database")
async def query_database(request: QueryDatabaseRequest):
    """Query MongoDB collection"""
    try:
        cursor = db[request.collection].find(request.filter, request.projection).limit(request.limit)
        documents = await cursor.to_list(length=request.limit)
        
        # Convert ObjectId to string
        for doc in documents:
            if "_id" in doc:
                doc["_id"] = str(doc["_id"])
        
        return {
            "success": True,
            "data": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Error querying database: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/tools/count_documents")
async def count_documents(request: CountDocumentsRequest):
    """Count documents in collection"""
    try:
        count = await db[request.collection].count_documents(request.filter)
        return {"success": True, "count": count}
    except Exception as e:
        logger.error(f"Error counting documents: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tools/list_collections")
async def list_collections():
    """List all collections"""
    try:
        collections = await db.list_collection_names()
        return {"success": True, "collections": collections}
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tools/get_collection_schema/{collection}")
async def get_collection_schema(collection: str):
    """Get collection schema sample"""
    try:
        doc = await db[collection].find_one()
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return {"success": True, "schema": doc or {}}
    except Exception as e:
        logger.error(f"Error getting collection schema: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# Update operations
@app.post("/tools/update_order")
async def update_order(request: UpdateOrderRequest):
    """Update fields of an order with validation"""
    try:
        # First verify that the order exists
        order = await db["newOrdini"].find_one({"orderId": request.order_id})
        
        if not order:
            logger.error(f"Order validation failed: {request.order_id} not found in database")
            raise HTTPException(
                status_code=404, 
                detail={
                    "error": f"Order {request.order_id} not found in database",
                    "message": "Please use a real order ID from the database"
                }
            )
        
        # Proceed with the update
        result = await db["newOrdini"].update_one(
            {"orderId": request.order_id},
            {"$set": request.updates}
        )
        
        return {
            "success": True,
            "modified_count": result.modified_count,
            "order_id": request.order_id,
            "updates_applied": request.updates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/update_order_priority")
async def update_order_priority(request: UpdateOrderPriorityRequest):
    """Update order priority with validation"""
    try:
        # Verify order exists
        order = await db["newOrdini"].find_one({"orderId": request.order_id})
        
        if not order:
            logger.error(f"Priority update failed: Order {request.order_id} not found")
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Order {request.order_id} not found",
                    "message": "Cannot update priority for non-existent order"
                }
            )
        
        # Update priority
        result = await db["newOrdini"].update_one(
            {"orderId": request.order_id},
            {"$set": {"priority": request.priority}}
        )
        
        return {
            "success": True,
            "modified_count": result.modified_count,
            "order_id": request.order_id,
            "new_priority": request.priority
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating order priority: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/update_machine")
async def update_machine(request: UpdateMachineRequest):
    """Update machine settings"""
    try:
        # Convert string ID to ObjectId
        machine_id = ObjectId(request.machine_id) if ObjectId.is_valid(request.machine_id) else request.machine_id
        
        # Verify machine exists
        machine = await db["macchinari"].find_one({"_id": machine_id})
        
        if not machine:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Machine {request.machine_id} not found",
                    "message": "Cannot update non-existent machine"
                }
            )
        
        # Update machine
        result = await db["macchinari"].update_one(
            {"_id": machine_id},
            {"$set": request.updates}
        )
        
        return {
            "success": True,
            "modified_count": result.modified_count,
            "machine_id": request.machine_id,
            "updates_applied": request.updates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating machine: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/add_order_note")
async def add_order_note(request: AddOrderNoteRequest):
    """Add a note to an order"""
    try:
        # Verify order exists
        order = await db["newOrdini"].find_one({"orderId": request.order_id})
        
        if not order:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": f"Order {request.order_id} not found",
                    "message": "Cannot add note to non-existent order"
                }
            )
        
        # Add note with timestamp
        note = {
            "text": request.note,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "MCP_action"
        }
        
        result = await db["newOrdini"].update_one(
            {"orderId": request.order_id},
            {"$push": {"notes": note}}
        )
        
        return {
            "success": True,
            "modified_count": result.modified_count,
            "order_id": request.order_id,
            "note_added": note
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding order note: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/add_machine_staff")
async def add_machine_staff(request: AddMachineStaffRequest):
    """Assign additional operators to a machine"""
    try:
        machine_id = ObjectId(request.machine_id) if ObjectId.is_valid(request.machine_id) else request.machine_id
        
        # Add staff to operators array
        result = await db["macchinari"].update_one(
            {"_id": machine_id},
            {"$addToSet": {"operators": {"$each": request.staff}}}
        )
        
        return {
            "success": True,
            "modified_count": result.modified_count,
            "machine_id": request.machine_id,
            "staff_added": request.staff
        }
        
    except Exception as e:
        logger.error(f"Error adding machine staff: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/reschedule_machine_orders")
async def reschedule_machine_orders(request: RescheduleOrdersRequest):
    """Reschedule all orders for a machine"""
    try:
        result = await db["newOrdini"].update_many(
            {"machine": request.machine_id},
            {"$set": request.schedule}
        )
        
        return {
            "success": True,
            "modified_count": result.modified_count,
            "machine_id": request.machine_id,
            "schedule_applied": request.schedule
        }
        
    except Exception as e:
        logger.error(f"Error rescheduling orders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting MCP server on port {PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)