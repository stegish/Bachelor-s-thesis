from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging
from ...domain.interfaces.recommendation_repository import IRecommendationRepository
from ...domain.entities.llm_recommendation import LLMRecommendation

logger = logging.getLogger(__name__)

class MongoRecommendationRepository(IRecommendationRepository):
    """MongoDB implementation of recommendation repository"""
    
    def __init__(self, connection_string: str, database_name: str = "AI-manager"):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client[database_name]
        self.collection = self.db["LLM-recommendations"]
        logger.info(f"Connected to {database_name}.LLM-recommendations collection")
    
    async def save_recommendation(self, recommendation: LLMRecommendation) -> str:
        """Save recommendation to MongoDB"""
        try:
            doc = recommendation.to_dict()
            result = await self.collection.insert_one(doc)
            logger.info(f"Saved recommendation with ID: {recommendation.analysis_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving recommendation: {str(e)}")
            raise
    
    async def get_latest_recommendation(self) -> Optional[LLMRecommendation]:
        """Get the most recent recommendation"""
        try:
            doc = await self.collection.find_one(
                {},
                sort=[("timestamp", -1)]
            )
            if doc:
                return self._document_to_entity(doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching latest recommendation: {str(e)}")
            return None
    
    async def get_recommendations_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[LLMRecommendation]:
        """Get recommendations within date range"""
        try:
            cursor = self.collection.find({
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }).sort("timestamp", -1)
            
            recommendations = []
            async for doc in cursor:
                recommendation = self._document_to_entity(doc)
                if recommendation:
                    recommendations.append(recommendation)
            
            return recommendations
        except Exception as e:
            logger.error(f"Error fetching recommendations by date range: {str(e)}")
            return []
    
    async def get_recommendation_by_id(self, analysis_id: str) -> Optional[LLMRecommendation]:
        """Get specific recommendation by ID"""
        try:
            doc = await self.collection.find_one({"analysis_id": analysis_id})
            if doc:
                return self._document_to_entity(doc)
            return None
        except Exception as e:
            logger.error(f"Error fetching recommendation {analysis_id}: {str(e)}")
            return None
    
    def _document_to_entity(self, doc: Dict[str, Any]) -> Optional[LLMRecommendation]:
        """Convert MongoDB document to entity"""
        try:
            return LLMRecommendation(
                analysis_id=doc.get('analysis_id'),
                timestamp=doc.get('timestamp'),
                prompt_used=doc.get('prompt_used'),
                context_data=doc.get('context_data', {}),
                analysis=doc.get('analysis'),
                recommendations=doc.get('recommendations', []),
                metrics_analyzed=doc.get('metrics_analyzed', {}),
                anomalies_detected=doc.get('anomalies_detected', []),
                priority_actions=doc.get('priority_actions', []),
                data_sources=doc.get('data_sources', []),
                model_used=doc.get('model_used'),
                processing_time=doc.get('processing_time', 0),
                created_at=doc.get('created_at', datetime.now())
            )
        except Exception as e:
            logger.error(f"Error converting document to entity: {str(e)}")
            return None