from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from ....domain.interfaces.repository import IOrderRepository, IMachineRepository, IAnalyticsRepository
from ....domain.entities import Order, Machine, AnalyticsResult
from .mappers import OrderMapper, MachineMapper, AnalyticsMapper
import logging

logger = logging.getLogger(__name__)

class OrderRepository(IOrderRepository):
    def __init__(self, client: AsyncIOMotorClient, database_name: str):
        self.client = client
        self.db = client[database_name]
        self.collection = self.db.newOrdini
        self.mapper = OrderMapper()
    
    async def get_all(self, limit: Optional[int] = None) -> List[Order]:
        """Get all orders, skipping any that fail to parse"""
        try:
            # Check if collection exists
            collections = await self.db.list_collection_names()
            if 'newOrdini' not in collections:
                logger.warning(f"Collection 'newOrdini' not found in database '{self.db.name}'")
                return []
            
            cursor = self.collection.find({})
            if limit:
                cursor = cursor.limit(limit)
            
            orders = []
            skipped = 0
            processed = 0
            
            async for doc in cursor:
                processed += 1
                try:
                    order = self.mapper.to_domain(doc)
                    if order:
                        orders.append(order)
                    else:
                        skipped += 1
                        logger.warning(f"Skipped order with ID: {doc.get('orderId', 'unknown')}")
                except Exception as e:
                    skipped += 1
                    logger.error(f"Error processing order {doc.get('orderId', 'unknown')}: {e}")
            
            logger.info(f"Processed {processed} documents: {len(orders)} valid orders, {skipped} skipped")
            
            return orders
            
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return []
    
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID"""
        try:
            doc = await self.collection.find_one({"orderId": order_id})
            if doc:
                return self.mapper.to_domain(doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {e}")
            return None
    
    async def get_by_status(self, status: int) -> List[Order]:
        """Get orders by status"""
        try:
            docs = await self.collection.find({"orderStatus.$numberInt": str(status)}).to_list(None)
            orders = []
            
            for doc in docs:
                order = self.mapper.to_domain(doc)
                if order:
                    orders.append(order)
            
            return orders
        except Exception as e:
            logger.error(f"Error fetching orders by status {status}: {e}")
            return []
    
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Order]:
        """Get orders within date range"""
        try:
            start_timestamp = int(start_date.timestamp() * 1000)
            end_timestamp = int(end_date.timestamp() * 1000)
            
            docs = await self.collection.find({
                "orderInsertDate.$date.$numberLong": {
                    "$gte": str(start_timestamp),
                    "$lte": str(end_timestamp)
                }
            }).to_list(None)
            
            orders = []
            for doc in docs:
                order = self.mapper.to_domain(doc)
                if order:
                    orders.append(order)
            
            return orders
        except Exception as e:
            logger.error(f"Error fetching orders by date range: {e}")
            return []

class MachineRepository(IMachineRepository):
    def __init__(self, client: AsyncIOMotorClient, database_name: str):
        self.client = client
        self.db = client[database_name]
        self.collection = self.db.macchinari
        self.mapper = MachineMapper()
    
    async def get_all(self) -> List[Machine]:
        """Get all machines, skipping any that fail to parse"""
        try:
            # Check if collection exists
            collections = await self.db.list_collection_names()
            if 'macchinari' not in collections:
                logger.warning(f"Collection 'macchinari' not found in database '{self.db.name}'")
                return []
            
            docs = await self.collection.find({}).to_list(None)
            machines = []
            skipped = 0
            
            for doc in docs:
                try:
                    machine = self.mapper.to_domain(doc)
                    if machine:
                        machines.append(machine)
                    else:
                        skipped += 1
                        logger.warning(f"Skipped machine: {doc.get('name', 'unknown')}")
                except Exception as e:
                    skipped += 1
                    logger.error(f"Error processing machine {doc.get('name', 'unknown')}: {e}")
            
            logger.info(f"Processed {len(docs)} documents: {len(machines)} valid machines, {skipped} skipped")
            
            return machines
        except Exception as e:
            logger.error(f"Error fetching machines: {e}")
            return []
    
    async def get_by_name(self, name: str) -> Optional[Machine]:
        """Get machine by name"""
        try:
            doc = await self.collection.find_one({"name": name})
            if doc:
                return self.mapper.to_domain(doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching machine {name}: {e}")
            return None
    
    async def get_active_machines(self) -> List[Machine]:
        """Get active machines"""
        try:
            docs = await self.collection.find({"macchinarioActive": True}).to_list(None)
            machines = []
            
            for doc in docs:
                machine = self.mapper.to_domain(doc)
                if machine:
                    machines.append(machine)
            
            return machines
        except Exception as e:
            logger.error(f"Error fetching active machines: {e}")
            return []

class AnalyticsRepository(IAnalyticsRepository):
    def __init__(self, client: AsyncIOMotorClient, database_name: str):
        self.client = client
        self.db = client[database_name]
        self.collection = self.db.analytics_results
        self.mapper = AnalyticsMapper()
    
    async def save_result(self, result: AnalyticsResult) -> None:
        """Save analytics result"""
        try:
            doc = self.mapper.to_document(result)
            await self.collection.insert_one(doc)
            logger.info("Analytics result saved successfully")
        except Exception as e:
            logger.error(f"Error saving analytics result: {e}")
            raise
    
    async def get_latest_result(self) -> Optional[AnalyticsResult]:
        """Get latest analytics result"""
        try:
            doc = await self.collection.find_one(
                sort=[("timestamp", -1)]
            )
            if doc:
                return self.mapper.to_domain(doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching latest analytics result: {e}")
            return None
    
    async def get_results_by_date_range(self, start_date: datetime, end_date: datetime) -> List[AnalyticsResult]:
        """Get analytics results within date range"""
        try:
            docs = await self.collection.find({
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }).to_list(None)
            
            results = []
            for doc in docs:
                result = self.mapper.to_domain(doc)
                if result:
                    results.append(result)
            
            return results
        except Exception as e:
            logger.error(f"Error fetching analytics results by date range: {e}")
            return []