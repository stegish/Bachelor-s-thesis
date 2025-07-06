from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

class MongoDBRepository:
    """Simple MongoDB repository used by the MCP server."""

    def __init__(self, uri: str, database_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[database_name]
        # Additional DB containing company settings
        self.company_db = self.client.get_database("azienda")

    async def find_documents(
        self, collection: str, filter: Dict[str, Any], limit: int, projection: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        cursor = self.db[collection].find(filter, projection).limit(limit)
        return await cursor.to_list(length=limit)

    async def count_documents(self, collection: str, filter: Dict[str, Any]) -> int:
        return await self.db[collection].count_documents(filter)

    async def list_collections(self) -> List[str]:
        return await self.db.list_collection_names()

    async def get_schema_sample(self, collection: str) -> Dict[str, Any]:
        doc = await self.db[collection].find_one()
        return doc or {}

    async def insert_order(self, order: Dict[str, Any]) -> str:
        result = await self.db["newOrdini"].insert_one(order)
        return str(result.inserted_id)

    async def add_machine_staff(self, machine_id: str, staff: List[str]) -> int:
        update = {"$addToSet": {"operators": {"$each": staff}}}
        result = await self.db["macchinari"].update_one({"_id": ObjectId(machine_id)}, update)
        return result.modified_count

    async def reschedule_machine_orders(self, machine_id: str, schedule: Dict[str, Any]) -> int:
        result = await self.db["newOrdini"].update_many({"machine": machine_id}, {"$set": schedule})
        return result.modified_count

    async def get_working_hours(self) -> Dict[str, Any]:
        settings = await self.company_db["settings"].find_one({})
        shifts = await self.company_db["turni"].find().to_list(length=None)
        return {"settings": settings, "turni": shifts}

    @app.post("/tools/update_order")
    async def update_order(request: UpdateOrderRequest):
        """Update fields of an order with validation"""
        try:
            # Prima verifica che l'ordine esista
            order = await mongo_repo.find_documents(
                collection="newOrdini",
                filter={"orderId": request.order_id},
                limit=1
            )
            
            if not order:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Order {request.order_id} not found in database. Please use a real order ID."
                )
            
            # Poi esegui l'update
            modified = await mongo_repo.update_order_fields(request.order_id, request.updates)
            
            # Log per debug
            logger.info(f"Updated order {request.order_id}: {request.updates}, modified: {modified}")
            
            return {
                "success": True, 
                "modified": modified,
                "order_id": request.order_id,
                "message": f"Successfully updated order {request.order_id}"
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating order: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
    

    async def update_phase_fields(self, order_id: str, phase_id: str, updates: Dict[str, Any]) -> int:
        """Update fields within a specific phase of an order"""
        set_updates = {f"Phases.$.{k}": v for k, v in updates.items()}
        result = await self.db["newOrdini"].update_one(
            {"orderId": order_id, "Phases.phaseId": phase_id},
            {"$set": set_updates}
        )
        return result.modified_count

    async def add_order_note(self, order_id: str, note: Dict[str, Any]) -> int:
        """Append a note to an order"""
        result = await self.db["newOrdini"].update_one({"orderId": order_id}, {"$push": {"notes": note}})
        return result.modified_count

    @app.post("/tools/update_machine")
    async def update_machine(request: UpdateMachineRequest):
        """Update machine settings with validation"""
        try:
            from bson import ObjectId
            
            # Valida che sia un ObjectId valido
            try:
                machine_oid = ObjectId(request.machine_id)
            except:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid machine ID format. Must be a valid MongoDB ObjectId."
                )
            
            # Verifica che la macchina esista
            machine = await mongo_repo.find_documents(
                collection="macchinari",
                filter={"_id": machine_oid},
                limit=1
            )
            
            if not machine:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Machine {request.machine_id} not found. Please use a real machine ID from the database."
                )
            
            # Esegui l'update
            modified = await mongo_repo.update_machine(request.machine_id, request.updates)
            
            logger.info(f"Updated machine {request.machine_id} ({machine[0].get('macchinarioName', 'Unknown')}): {request.updates}")
            
            return {
                "success": True, 
                "modified": modified,
                "machine_id": request.machine_id,
                "machine_name": machine[0].get('macchinarioName', 'Unknown'),
                "message": f"Successfully updated machine {machine[0].get('macchinarioName', 'Unknown')}"
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating machine: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        
    async def verify_update(self, collection: str, filter_dict: Dict[str, Any], expected_values: Dict[str, Any]) -> bool:
        """Verify that an update was applied successfully"""
        doc = await self.db[collection].find_one(filter_dict)
        if not doc:
            return False
        
        for key, expected_value in expected_values.items():
            if key not in doc or doc[key] != expected_value:
                return False

        return True

    async def update_shift(self, shift_id: str, updates: Dict[str, Any]) -> int:
        """Update a shift document in the company DB"""
        result = await self.company_db["turni"].update_one({"_id": ObjectId(shift_id)}, {"$set": updates})
        return result.modified_count
