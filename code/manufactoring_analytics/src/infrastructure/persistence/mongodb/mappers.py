from typing import Dict, Any, Optional, List
from datetime import datetime
from ....domain.entities import Order, Machine, AnalyticsResult, Phase
from ....domain.value_objects import OrderStatus, PhaseStatus
import logging

logger = logging.getLogger(__name__)

class OrderMapper:
    def to_domain(self, doc: Dict[str, Any]) -> Optional[Order]:
        """Convert MongoDB document to Order domain entity"""
        try:
            # Extract phases
            phases = []
            for phase_doc in doc.get('Phases', []):
                try:
                    phase = self._parse_phase(phase_doc)
                    if phase:
                        phases.append(phase)
                except Exception as e:
                    logger.warning(f"Failed to parse phase in order {doc.get('orderId', 'unknown')}: {e}")
                    continue
            
            order = Order(
                order_id=str(doc.get('orderId', '')),
                article_code=str(doc.get('codiceArticolo', '')),
                product_family=str(doc.get('famigliaDiProdotto', '')),
                quantity=self._get_int_value(doc.get('quantity', 0)),
                priority=self._get_int_value(doc.get('priority', 0)),
                status=OrderStatus.from_value(self._get_int_value(doc.get('orderStatus', 0))),
                phases=phases,
                insert_date=self._parse_date(doc.get('orderInsertDate')),
                start_date=self._parse_date(doc.get('orderStartDate')),
                deadline=self._parse_date(doc.get('orderDeadline')),
                real_finish_date=self._parse_date(doc.get('realOrderFinishDate')) or self._parse_date(doc.get('realFinishDate'))
            )
            
            return order
            
        except Exception as e:
            logger.error(f"Failed to parse order {doc.get('orderId', 'unknown')}: {e}")
            return None
    
    def _parse_phase(self, phase_doc: Dict[str, Any]) -> Optional[Phase]:
        """Parse a single phase document"""
        try:
            # Handle declaredQuantity that can be null
            declared_quantity = phase_doc.get('declaredQuantity')
            if declared_quantity is None:
                declared_quantity = 0
            else:
                declared_quantity = self._get_int_value(declared_quantity)
            
            # Ensure operators is always a list
            operators = phase_doc.get('operators', [])
            if not isinstance(operators, list):
                operators = []
            
            phase = Phase(
                phase_id=str(phase_doc.get('phaseId', '')),
                name=str(phase_doc.get('phaseName', '')),
                status=PhaseStatus.from_value(self._get_int_value(phase_doc.get('phaseStatus', 0))),
                cycle_time=self._get_int_value(phase_doc.get('cycleTime', 0)),
                phase_real_time=self._get_int_value(phase_doc.get('phaseRealTime', 0)),
                declared_quantity=declared_quantity,
                operators=operators,
                queue_insert_date=self._parse_date(phase_doc.get('queueInsertDate')),
                queue_real_insert_date=self._parse_date(phase_doc.get('queueRealInsertDate')),
                finish_date=self._parse_date(phase_doc.get('finishDate')),
                real_finish_date=self._parse_date(phase_doc.get('realFinishDate'))
            )
            
            return phase
            
        except Exception as e:
            logger.warning(f"Failed to parse phase {phase_doc.get('phaseId', 'unknown')}: {e}")
            return None
    
    def _get_int_value(self, value: Any) -> int:
        """Extract integer value from MongoDB format or direct integer"""
        try:
            if value is None:
                return 0
            elif isinstance(value, int):
                return value
            elif isinstance(value, float):
                return int(value)
            elif isinstance(value, str):
                # Handle string numbers
                value = value.strip()
                if value.isdigit():
                    return int(value)
                elif value.replace('.', '', 1).isdigit():
                    return int(float(value))
                else:
                    return 0
            elif isinstance(value, dict):
                if '$numberInt' in value:
                    return int(value['$numberInt'])
                elif '$numberLong' in value:
                    return int(value['$numberLong'])
            return 0
        except Exception as e:
            logger.debug(f"Failed to parse int value {value}: {e}")
            return 0
    
    def _parse_date(self, date_obj: Any) -> Optional[datetime]:
        """Parse date from MongoDB format"""
        try:
            if not date_obj:
                return None
            
            # Handle if it's already a datetime object
            if isinstance(date_obj, datetime):
                return date_obj
            
            # Handle string dates
            if isinstance(date_obj, str):
                try:
                    return datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
                except:
                    return None
            
            # Handle MongoDB date format
            if isinstance(date_obj, dict) and '$date' in date_obj:
                date_value = date_obj['$date']
                
                # Handle nested $numberLong
                if isinstance(date_value, dict) and '$numberLong' in date_value:
                    timestamp = int(date_value['$numberLong'])
                    return datetime.fromtimestamp(timestamp / 1000)
                
                # Handle direct timestamp
                elif isinstance(date_value, (int, str)):
                    timestamp = int(date_value)
                    return datetime.fromtimestamp(timestamp / 1000)
            
            return None
            
        except Exception as e:
            logger.debug(f"Failed to parse date {date_obj}: {e}")
            return None

class MachineMapper:
    def to_domain(self, doc: Dict[str, Any]) -> Optional[Machine]:
        """Convert MongoDB document to Machine domain entity"""
        try:
            machine = Machine(
                name=str(doc.get('name', '')),
                is_active=bool(doc.get('macchinarioActive', False)),
                queue_target_time=self._get_int_value(doc.get('queueTargetTime', 0)),
                current_queue=doc.get('tablet', []) or []
            )
            
            return machine
            
        except Exception as e:
            logger.error(f"Failed to parse machine {doc.get('name', 'unknown')}: {e}")
            return None
    
    def _get_int_value(self, value: Any) -> int:
        """Extract integer value from MongoDB format or direct integer"""
        try:
            if value is None:
                return 0
            elif isinstance(value, int):
                return value
            elif isinstance(value, float):
                return int(value)
            elif isinstance(value, str):
                # Handle string numbers
                value = value.strip()
                if value.isdigit():
                    return int(value)
                elif value.replace('.', '', 1).isdigit():
                    return int(float(value))
                else:
                    return 0
            elif isinstance(value, dict):
                if '$numberInt' in value:
                    return int(value['$numberInt'])
                elif '$numberLong' in value:
                    return int(value['$numberLong'])
            return 0
        except Exception as e:
            logger.debug(f"Failed to parse int value {value}: {e}")
            return 0

class AnalyticsMapper:
    def to_domain(self, doc: Dict[str, Any]) -> Optional[AnalyticsResult]:
        """Convert MongoDB document to AnalyticsResult domain entity"""
        try:
            result = AnalyticsResult(
                timestamp=doc.get('timestamp', datetime.now()),
                total_orders=int(doc.get('total_orders', 0)),
                completed_orders=int(doc.get('completed_orders', 0)),
                active_machines=int(doc.get('active_machines', 0)),
                total_machines=int(doc.get('total_machines', 0)),
                avg_order_lead_time=float(doc.get('avg_order_lead_time', 0.0)),
                on_time_delivery_rate=float(doc.get('on_time_delivery_rate', 0.0)),
                avg_machine_utilization=float(doc.get('avg_machine_utilization', 0.0)),
                avg_machine_efficiency=float(doc.get('avg_machine_efficiency', 0.0)),
                total_operators=int(doc.get('total_operators', 0)),
                bottleneck_machines=doc.get('bottleneck_machines', []) or [],
                files_generated=doc.get('files_generated', {}) or {}
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to parse analytics result: {e}")
            return None
    
    def to_document(self, result: AnalyticsResult) -> Dict[str, Any]:
        """Convert AnalyticsResult to MongoDB document"""
        try:
            return {
                'timestamp': result.timestamp,
                'total_orders': result.total_orders,
                'completed_orders': result.completed_orders,
                'active_machines': result.active_machines,
                'total_machines': result.total_machines,
                'avg_order_lead_time': result.avg_order_lead_time,
                'on_time_delivery_rate': result.on_time_delivery_rate,
                'avg_machine_utilization': result.avg_machine_utilization,
                'avg_machine_efficiency': result.avg_machine_efficiency,
                'total_operators': result.total_operators,
                'bottleneck_machines': result.bottleneck_machines,
                'files_generated': result.files_generated
            }
        except Exception as e:
            logger.error(f"Failed to convert analytics result to document: {e}")
            raise