import uuid
import httpx
import json
from datetime import datetime
from typing import Dict, Any, List
import logging
import re
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
            
            # 3. Prepare the analysis prompt - DEFINISCI PROMPT QUI
            prompt = custom_prompt or self._get_default_analysis_prompt()
            
            # 4. Add MCP capabilities to context
            mcp_capabilities = {
                'mcp_available': True,
                'executable_actions': [
                    'update_order_priority',
                    'update_order',
                    'update_machine',
                    'add_order_note',
                    'reschedule_orders',
                    'add_machine_staff'
                ],
                'note': 'You can propose these actions and they will be executed after user approval'
            }
            
            # 5. Create analysis request with all context
            request = AnalysisRequest(
                question=prompt,
                context_data={
                    'csv_analytics': csv_data,
                    'mongodb_context': mongodb_context,
                    'mcp_capabilities': mcp_capabilities,
                    'analysis_timestamp': datetime.now().isoformat()
                },
                include_db_context=True
            )
            
            # 6. Get LLM analysis
            logger.info("Sending request to LLM with MCP capabilities in context")
            analysis_result = await self.llm_service.analyze(request)
            
            # Log per debug
            logger.info("LLM Analysis Result (first 1000 chars):")
            logger.info(analysis_result.answer[:1000])
            
            # 7. Parse recommendations from analysis
            recommendations = self._parse_recommendations(analysis_result.answer)
            anomalies = self._extract_anomalies(analysis_result.answer)
            priority_actions = self._extract_priority_actions(analysis_result.answer)
            
            # Log extracted actions
            logger.info(f"Extracted priority actions: {priority_actions}")
            
            # 8. Extract metrics from CSV data
            metrics = self._extract_key_metrics(csv_data)
            
            # 9. Create recommendation entity
            recommendation = LLMRecommendation(
                analysis_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                prompt_used=prompt,  # ORA PROMPT È DEFINITO
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
            
            # 10. Save to MongoDB
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
        """Get default comprehensive analysis prompt with real ID usage"""
        return """
        CONTEXT: You are analyzing manufacturing data and have the ability to propose executable actions through the Manufacturing Control Platform (MCP). These actions can directly modify the production database to fix issues.
        
        ⚠️ CRITICAL: You MUST use REAL IDs from the data provided. DO NOT use example IDs like "ABC123" or "XYZ456".
        
        Your proposed actions will be:
        1. Shown to the user for approval
        2. Executed automatically upon approval
        3. Applied directly to the MongoDB database
        
        Perform a comprehensive analysis of the current manufacturing state using all available data.
        
        1. **Current Production Status**
        - Overall efficiency and utilization rates
        - Order completion rates and delays
        - Current bottlenecks and constraints
        - IDENTIFY REAL ORDER IDs that are causing delays
        
        2. **Anomaly Detection**
        - Identify any unusual patterns or deviations
        - Flag machines with abnormal performance
        - Highlight unexpected delays or inefficiencies
        - LIST SPECIFIC ORDER IDs and MACHINE IDs involved
        
        3. **Critical Issues**
        - List top 5 most critical issues requiring immediate attention
        - Include REAL ORDER IDs and MACHINE IDs from the data
        - Explain the impact of each issue
        - Provide risk assessment
        
        4. **Recommendations**
        - Provide 5-7 specific, actionable recommendations
        - Prioritize by impact and urgency
        - Include expected outcomes for each recommendation
        
        5. **Priority Actions for MCP Execution**
        
        ⚠️ CRITICAL FORMAT INSTRUCTIONS ⚠️
        
        RULES FOR ACTIONS:
        1. ONLY use order IDs that you can see in the data (e.g., "hyvjyhj_1", "xyz_order_123")
        2. ONLY use machine IDs from MongoDB (24-character ObjectIds like "678e38af83411cc4eac7bf51")
        3. Look for orders with high delays, low priority, or blocking status
        4. Each action MUST reference REAL data, not examples
        
        FORMAT: Each action on ONE line:
        URGENT: [Real issue from data]. Action: [command] Parameters: {"key": "REAL_VALUE_FROM_DATA"}
        
        Example with REAL data (adapt to what you see):
        URGENT: Order hyvjyhj_1 has 500 hour delay blocking machine TAGLIO. Action: update_order_priority Parameters: {"order_id": "hyvjyhj_1", "priority": 1}
        
        Available MCP commands:
        • update_order_priority - Change order priority (use REAL orderId from data)
        • update_order - Update any order field (use REAL orderId)
        • update_machine - Update machine settings (use REAL MongoDB ObjectId)
        • add_order_note - Add note to order (use REAL orderId)
        • reschedule_orders - Reschedule machine queue (use REAL machine ObjectId)
        
        VERIFICATION before proposing action:
        ✓ Is this a REAL order/machine ID from the provided data?
        ✓ Have I verified this ID exists in the context?
        ✓ Will this action help solve a REAL problem I identified?
        
        DO NOT PROPOSE ACTIONS WITH FAKE IDs - ONLY USE IDs YOU CAN SEE IN THE DATA!
        
        6. **Predictive Insights**
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
        """Extract priority actions from analysis with improved parsing."""
        import re
        import json
        
        actions = []
        lines = analysis.split("\n")
        
        # Multiple patterns to catch different formats
        patterns = [
            # Original format
            r'(URGENT|CRITICAL|PRIORITY):\s*(.+?)\s*Action:\s*(\S+)\s*Parameters:\s*(\{.+?\})',
            # Format with period before Action
            r'(URGENT|CRITICAL|PRIORITY):\s*(.+?)\.\s*Action:\s*(\S+)\s*Parameters:\s*(\{.+?\})',
            # Format with newlines
            r'(URGENT|CRITICAL|PRIORITY):\s*(.+?)\n?\s*Action:\s*(\S+)\n?\s*Parameters:\s*(\{.+?\})',
            # More flexible format
            r'(URGENT|CRITICAL|PRIORITY)[:\s]+(.+?)\s+Action[:\s]+(\S+)\s+Parameters[:\s]+(\{.+?\})'
        ]
        
        action_count = 0
        processed_lines = set()  # Track processed lines to avoid duplicates
        
        # Try each pattern
        for pattern in patterns:
            for i, line in enumerate(lines):
                if i in processed_lines:
                    continue
                    
                # Also check multi-line by joining with next line
                extended_line = line
                if i + 1 < len(lines):
                    extended_line = line + " " + lines[i + 1]
                
                for text in [line, extended_line]:
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    
                    if match:
                        processed_lines.add(i)
                        if i + 1 < len(lines) and text == extended_line:
                            processed_lines.add(i + 1)
                        
                        action_count += 1
                        urgency = match.group(1).lower()
                        description = match.group(2).strip().rstrip('.')
                        command = match.group(3).strip()
                        params_str = match.group(4).strip()
                        
                        logger.info(f"Found action: urgency={urgency}, command={command}, params={params_str}")
                        
                        # Try to parse JSON parameters
                        parameters = None
                        try:
                            parameters = json.loads(params_str)
                        except json.JSONDecodeError:
                            # Try fixing common JSON errors
                            try:
                                # Replace single quotes with double quotes
                                fixed_params = params_str.replace("'", '"')
                                parameters = json.loads(fixed_params)
                            except:
                                # Try adding quotes to unquoted keys/values
                                try:
                                    # Simple regex to add quotes to unquoted strings
                                    fixed_params = re.sub(r'(\w+):', r'"\1":', params_str)
                                    fixed_params = re.sub(r':\s*([a-zA-Z_]\w*)', r': "\1"', fixed_params)
                                    parameters = json.loads(fixed_params)
                                except:
                                    logger.warning(f"Failed to parse parameters: {params_str}")
                        
                        # Handle special cases for common actions
                        if not parameters and command == "update_order_priority":
                            # Try to extract order_id and priority from description
                            order_match = re.search(r'order[:\s]+(\S+)', description, re.IGNORECASE)
                            priority_match = re.search(r'priority[:\s]+(\d+)', description, re.IGNORECASE)
                            if order_match and priority_match:
                                parameters = {
                                    "order_id": order_match.group(1),
                                    "priority": int(priority_match.group(1))
                                }
                        
                        action_dict = {
                            "id": f"ACTION-{action_count:03d}",
                            "description": description,
                            "urgency": urgency,
                            "estimated_impact": "High" if urgency in ["critical", "urgent"] else "Medium",
                            "action": command,
                            "parameters": parameters or {}
                        }
                        
                        # Only add if we have valid action and parameters
                        if action_dict["action"] and action_dict["parameters"]:
                            actions.append(action_dict)
                            logger.info(f"Successfully parsed action: {action_dict}")
                        else:
                            logger.warning(f"Skipping action without valid command/parameters: {description}")
                        
                        break  # Found match, skip other patterns for this line
        
        # Fallback: Look for simpler action statements
        if not actions:
            logger.warning("No actions found with primary patterns, trying simple format")
            
            action_keywords = ["update", "change", "modify", "set", "reschedule", "add", "assign"]
            urgency_keywords = ["urgent", "critical", "priority", "immediately", "asap"]
            
            for line in lines:
                line_lower = line.lower()
                
                # Check if line contains urgency and action keywords
                has_urgency = any(keyword in line_lower for keyword in urgency_keywords)
                has_action = any(keyword in line_lower for keyword in action_keywords)
                
                if has_urgency and has_action:
                    # Try to extract meaningful action
                    action_count += 1
                    
                    # Determine action type based on keywords
                    action_type = None
                    if "priority" in line_lower and "order" in line_lower:
                        action_type = "update_order_priority"
                    elif "machine" in line_lower:
                        action_type = "update_machine"
                    elif "order" in line_lower:
                        action_type = "update_order"
                    
                    if action_type:
                        # Extract IDs using regex
                        id_match = re.search(r'[a-zA-Z0-9_]{6,}', line)
                        order_id = id_match.group(0) if id_match else None
                        
                        # Extract numbers for priority
                        num_match = re.search(r'\b(\d+)\b', line)
                        priority = int(num_match.group(1)) if num_match else 1
                        
                        if order_id:
                            action_dict = {
                                "id": f"ACTION-{action_count:03d}",
                                "description": line.strip(),
                                "urgency": "high",
                                "estimated_impact": "Medium",
                                "action": action_type,
                                "parameters": {
                                    "order_id": order_id,
                                    "priority": priority
                                } if action_type == "update_order_priority" else {
                                    "order_id": order_id,
                                    "updates": {}
                                }
                            }
                            actions.append(action_dict)
                            logger.info(f"Extracted simple action: {action_dict}")
        
        logger.info(f"Total actions extracted: {len(actions)}")
        return actions

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