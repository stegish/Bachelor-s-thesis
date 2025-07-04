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
