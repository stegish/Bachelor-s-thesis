# src/infrastructure/persistence/mongodb_context.py
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from ...domain.interfaces import IContextRepository
from ...domain.entities import AnalysisRequest, AnalysisResult
import logging

logger = logging.getLogger(__name__)

class MongoDBContextRepository(IContextRepository):
    """MongoDB implementation of context repository"""
    
    def __init__(self, connection_string: str, database_name: str):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[database_name]
        self.orders_collection = self.db['newOrdini']
        self.machines_collection = self.db['macchinari']
        self.history_collection = self.db['llm_analysis_history']
    
    async def get_context(self, question: str) -> Dict[str, Any]:
        """Retrieve relevant context based on question keywords"""
        context = {}
        keywords = question.lower()
        
        try:
            # Fetch relevant data based on keywords
            if any(word in keywords for word in ['order', 'production', 'status', 'delay']):
                orders = await self.get_orders_context(limit=50)
                if orders:
                    context['recent_orders'] = orders
            
            if any(word in keywords for word in ['machine', 'utilization', 'efficiency']):
                machines = await self.get_machines_context()
                if machines:
                    context['machines'] = machines
            
            # Get summary statistics
            if any(word in keywords for word in ['summary', 'overall', 'kpi', 'metric']):
                context['summary'] = await self._get_summary_stats()
                
        except Exception as e:
            logger.error(f"Error fetching context: {str(e)}")
        
        return context
    
    async def get_orders_context(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent orders"""
        cursor = self.orders_collection.find().limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_machines_context(self) -> List[Dict[str, Any]]:
        """Get all machines"""
        cursor = self.machines_collection.find()
        return await cursor.to_list(length=None)
    
    async def save_history(self, request: AnalysisRequest, result: AnalysisResult) -> None:
        """Save analysis to history"""
        document = {
            'question': request.question,
            'answer': result.answer,
            'timestamp': result.timestamp,
            'session_id': request.session_id,
            'model_used': result.model_used,
            'context_included': result.context_included,
            'files_processed': result.files_processed
        }
        
        await self.history_collection.insert_one(document)
    
    async def _get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics"""
        total_orders = await self.orders_collection.count_documents({})
        active_machines = await self.machines_collection.count_documents({'macchinarioActive': True})
        
        return {
            'total_orders': total_orders,
            'active_machines': active_machines,
            'total_machines': await self.machines_collection.count_documents({})
        }