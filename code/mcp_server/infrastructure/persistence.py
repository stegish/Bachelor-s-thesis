from typing import Any, Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient

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
        result = await self.db["macchinari"].update_one({"_id": machine_id}, update)
        return result.modified_count

    async def reschedule_machine_orders(self, machine_id: str, schedule: Dict[str, Any]) -> int:
        result = await self.db["newOrdini"].update_many({"machine": machine_id}, {"$set": schedule})
        return result.modified_count

    async def get_working_hours(self) -> Dict[str, Any]:
        settings = await self.company_db["settings"].find_one({})
        shifts = await self.company_db["turni"].find().to_list(length=None)
        return {"settings": settings, "turni": shifts}

    async def update_order_fields(self, order_id: str, updates: Dict[str, Any]) -> int:
        """Update top-level fields of an order"""
        result = await self.db["newOrdini"].update_one({"orderId": order_id}, {"$set": updates})
        return result.modified_count

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

    async def update_machine(self, machine_id: str, updates: Dict[str, Any]) -> int:
        """Update machine settings"""
        result = await self.db["macchinari"].update_one({"_id": machine_id}, {"$set": updates})
        return result.modified_count

    async def update_shift(self, shift_id: str, updates: Dict[str, Any]) -> int:
        """Update a shift document in the company DB"""
        result = await self.company_db["turni"].update_one({"_id": shift_id}, {"$set": updates})
        return result.modified_count
