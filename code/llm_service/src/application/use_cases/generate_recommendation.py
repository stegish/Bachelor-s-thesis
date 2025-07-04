import uuid
import httpx
import json
from datetime import datetime
from typing import Dict, Any, List
import logging
from ...domain.interfaces import ILLMService, IRecommendationRepository, IContextRepository
from ...domain.entities import AnalysisRequest, LLMRecommendation
from ..services import PromptBuilder

logger = logging.getLogger(__name__)

class GenerateRecommendationUseCase:
    """Use case for generating and saving LLM recommendations"""
    
    def __init__(
        self,
        llm_service: ILLMService,
        recommendation_repository: IRecommendationRepository,
        context_repository: IContextRepository,
        prompt_builder: PromptBuilder,
        analytics_api_url: str = "http://localhost:5000"
    ):
        self.llm_service = llm_service
        self.recommendation_repository = recommendation_repository
        self.context_repository = context_repository
        self.prompt_builder = prompt_builder
        self.analytics_api_url = analytics_api_url
    
    async def execute(self, custom_prompt: str = None) -> LLMRecommendation:
        """Generate recommendation from latest data and save to MongoDB"""
        start_time = datetime.now()
        
        try:
            # 1. Fetch latest CSV data from manufacturing analytics
            csv_data = await self._fetch_latest_csv_data()
            
            # 2. Get MongoDB context
            mongodb_context = await self.context_repository.get_context(
                "production status and anomalies"
            )
            
            # 3. Prepare the analysis prompt
            prompt = custom_prompt or self._get_default_analysis_prompt()
            
            # 4. Create analysis request with all context
            request = AnalysisRequest(
                question=prompt,
                context_data={
                    'csv_analytics': csv_data,
                    'mongodb_context': mongodb_context,
                    'analysis_timestamp': datetime.now().isoformat()
                },
                include_db_context=True
            )
            
            # 5. Get LLM analysis
            analysis_result = await self.llm_service.analyze(request)
            
            # 6. Parse recommendations from analysis
            recommendations = self._parse_recommendations(analysis_result.answer)
            anomalies = self._extract_anomalies(analysis_result.answer)
            priority_actions = self._extract_priority_actions(analysis_result.answer)
            
            # 7. Extract metrics from CSV data
            metrics = self._extract_key_metrics(csv_data)
            
            # 8. Create recommendation entity
            recommendation = LLMRecommendation(
                analysis_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                prompt_used=prompt,
                context_data={
                    'csv_files_analyzed': list(csv_data.keys()),
                    'mongodb_collections': list(mongodb_context.keys()),
                    'total_records_analyzed': sum(
                        data.get('row_count', 0) 
                        for data in csv_data.values() 
                        if isinstance(data, dict)
                    )
                },
                analysis=analysis_result.answer,
                recommendations=recommendations,
                metrics_analyzed=metrics,
                anomalies_detected=anomalies,
                priority_actions=priority_actions,
                data_sources=['manufacturing_analytics_csv', 'mongodb_direct'],
                model_used=analysis_result.model_used,
                processing_time=(datetime.now() - start_time).total_seconds()
            )
            
            # 9. Save to MongoDB
            await self.recommendation_repository.save_recommendation(recommendation)
            
            logger.info(f"Generated and saved recommendation: {recommendation.analysis_id}")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {str(e)}")
            raise
    
    async def _fetch_latest_csv_data(self) -> Dict[str, Any]:
        """Fetch latest CSV data from manufacturing analytics service"""
        try:
            async with httpx.AsyncClient() as client:
                # Get all CSV data as JSON
                response = await client.get(
                    f"{self.analytics_api_url}/api/v1/csv/download-all-json",
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Error fetching CSV data: {str(e)}")
            return {}
    
    def _get_default_analysis_prompt(self) -> str:
        """Get default comprehensive analysis prompt"""
        return """
        Perform a comprehensive analysis of the current manufacturing state using all available data.
        
        Your analysis should include:
        
        1. **Current Production Status**
           - Overall efficiency and utilization rates
           - Order completion rates and delays
           - Current bottlenecks and constraints
        
        2. **Anomaly Detection**
           - Identify any unusual patterns or deviations
           - Flag machines with abnormal performance
           - Highlight unexpected delays or inefficiencies
        
        3. **Critical Issues**
           - List top 5 most critical issues requiring immediate attention
           - Explain the impact of each issue
           - Provide risk assessment
        
        4. **Recommendations**
           - Provide 5-7 specific, actionable recommendations
           - Prioritize by impact and urgency
           - Include expected outcomes for each recommendation
        
        5. **Predictive Insights**
           - Predict potential issues in the next 24-48 hours
           - Suggest preventive measures
           - Identify trends that need monitoring
        
        Format your response with clear sections and bullet points for easy reading.
        Use specific numbers and percentages where available.
        """
    
    def _parse_recommendations(self, analysis: str) -> List[Dict[str, Any]]:
        """Parse recommendations from LLM analysis"""
        recommendations = []
        lines = analysis.split('\n')
        
        in_recommendations = False
        current_rec = {}
        rec_count = 0
        
        for line in lines:
            if 'recommendation' in line.lower() and ':' in line:
                in_recommendations = True
                continue
            
            if in_recommendations and line.strip():
                if line.strip()[0].isdigit() or line.strip().startswith('-'):
                    if current_rec:
                        recommendations.append(current_rec)
                    
                    rec_count += 1
                    current_rec = {
                        'id': f'REC-{rec_count:03d}',
                        'description': line.strip().lstrip('0123456789.-) '),
                        'priority': 'high' if rec_count <= 3 else 'medium',
                        'type': self._categorize_recommendation(line)
                    }
                elif current_rec and ':' in line:
                    # Additional details for current recommendation
                    key, value = line.split(':', 1)
                    current_rec[key.strip().lower()] = value.strip()
        
        if current_rec:
            recommendations.append(current_rec)
        
        return recommendations
    
    def _extract_anomalies(self, analysis: str) -> List[str]:
        """Extract detected anomalies from analysis"""
        anomalies = []
        lines = analysis.split('\n')
        
        keywords = ['anomaly', 'unusual', 'abnormal', 'unexpected', 'deviation', 'irregular']
        
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                anomalies.append(line.strip())
        
        return anomalies
    
    def _extract_priority_actions(self, analysis: str) -> List[Dict[str, Any]]:
        """Extract priority actions from analysis.

        The LLM is expected to mention lines containing actions to run via the MCP
        server using a format like::

            <description>. Action: <command> Parameters: {"key": "value"}

        Any line flagged as urgent/critical will be parsed and returned with the
        optional command and parameters for direct execution.
        """

        actions: List[Dict[str, Any]] = []
        lines = analysis.split("\n")

        priority_keywords = ["immediate", "urgent", "critical", "priority", "asap", "now"]
        action_count = 0

        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in priority_keywords):
                action_count += 1
                action_cmd = None
                params = None

                if "action:" in line_lower:
                    try:
                        after_action = line.split("action:", 1)[1]
                        if "parameters:" in after_action.lower():
                            action_part, param_part = after_action.split("parameters:", 1)
                        elif "params:" in after_action.lower():
                            action_part, param_part = after_action.split("params:", 1)
                        else:
                            action_part, param_part = after_action, ""

                        action_cmd = action_part.strip().strip(" ,")
                        param_part = param_part.strip().strip(" ,")
                        if param_part.startswith("{") and param_part.endswith("}"):
                            params = json.loads(param_part)
                    except Exception:
                        # If parsing fails just ignore command details
                        action_cmd = None
                        params = None

                actions.append({
                    "id": f"ACTION-{action_count:03d}",
                    "description": line.strip(),
                    "urgency": "critical" if any(k in line_lower for k in ["immediate", "critical"]) else "high",
                    "estimated_impact": "high",
                    "action": action_cmd,
                    "parameters": params,
                })

        return actions[:5]
    
    def _extract_key_metrics(self, csv_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract key metrics from CSV data"""
        metrics = {}
        
        # Extract from machine_metrics if available
        if 'machine_metrics' in csv_data:
            machine_data = csv_data['machine_metrics'].get('data', [])
            if machine_data:
                # Calculate utilization with None handling
                utilization_values = [m.get('utilization_percentage', 0) or 0 for m in machine_data]
                if utilization_values:
                    metrics['avg_machine_utilization'] = sum(utilization_values) / len(utilization_values)
                
                # Calculate efficiency with None handling
                efficiency_values = [m.get('efficiency_percentage', 0) or 0 for m in machine_data]
                if efficiency_values:
                    metrics['avg_machine_efficiency'] = sum(efficiency_values) / len(efficiency_values)
        
        # Extract from order_timeline if available
        if 'order_timeline' in csv_data:
            order_data = csv_data['order_timeline'].get('data', [])
            if order_data:
                completed = [o for o in order_data if o.get('order_status') == 4]
                on_time = [o for o in completed if o.get('on_time') == True]
                
                if order_data:
                    metrics['order_completion_rate'] = (len(completed) / len(order_data)) * 100
                
                if completed:
                    metrics['on_time_delivery_rate'] = (len(on_time) / len(completed)) * 100
                else:
                    metrics['on_time_delivery_rate'] = 0
        
        # Extract from queue_analysis if available
        if 'queue_analysis' in csv_data:
            queue_data = csv_data['queue_analysis'].get('data', [])
            if queue_data:
                # Handle None values in queue delays
                queue_delays = [q.get('avg_queue_delay', 0) or 0 for q in queue_data]
                if queue_delays:
                    metrics['avg_queue_delay_hours'] = sum(queue_delays) / len(queue_delays)
        
        return metrics
    
    def _categorize_recommendation(self, text: str) -> str:
        """Categorize recommendation type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['maintenance', 'repair', 'fix']):
            return 'maintenance'
        elif any(word in text_lower for word in ['optimize', 'improve', 'enhance']):
            return 'optimization'
        elif any(word in text_lower for word in ['alert', 'warning', 'critical']):
            return 'alert'
        else:
            return 'improvement'