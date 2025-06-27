from typing import List, Dict, Any
import pandas as pd
from ...domain.entities import Order

class OrderAnalyzer:
    """Service for analyzing order metrics following SRP"""
    
    def analyze_timeline(self, orders: List[Order]) -> pd.DataFrame:
        """Generate order timeline analysis"""
        timeline_data = []
        
        for order in orders:
            timeline_data.append({
                'order_id': order.order_id,
                'article_code': order.article_code,
                'product_family': order.product_family,
                'quantity': order.quantity,
                'priority': order.priority,
                'order_status': order.status.value,
                'insert_date': order.insert_date,
                'start_date': order.start_date,
                'deadline': order.deadline,
                'real_finish_date': order.real_finish_date,
                'lead_time_days': order.lead_time_days,
                'delay_days': order.delay_days,
                'on_time': order.is_on_time,
                'progress_percentage': order.progress_percentage,
                'total_phases': order.total_phases,
                'completed_phases': order.completed_phases
            })
        
        return pd.DataFrame(timeline_data)
    
    def analyze_performance(self, orders: List[Order]) -> Dict[str, Any]:
        """Analyze overall order performance"""
        if not orders:
            return self._empty_performance_metrics()
        
        completed_orders = [o for o in orders if o.is_completed]
        on_time_orders = [o for o in completed_orders if o.is_on_time]
        
        # Calculate average metrics
        lead_times = [o.lead_time_days for o in completed_orders if o.lead_time_days is not None]
        delays = [o.delay_days for o in completed_orders if o.delay_days is not None]
        
        return {
            'total_orders': len(orders),
            'completed_orders': len(completed_orders),
            'in_progress_orders': len([o for o in orders if not o.is_completed]),
            'completion_rate': (len(completed_orders) / len(orders) * 100) if orders else 0,
            'on_time_orders': len(on_time_orders),
            'on_time_rate': (len(on_time_orders) / len(completed_orders) * 100) if completed_orders else 0,
            'avg_lead_time_days': sum(lead_times) / len(lead_times) if lead_times else 0,
            'avg_delay_days': sum(delays) / len(delays) if delays else 0,
            'orders_by_status': self._count_by_status(orders),
            'orders_by_family': self._count_by_family(orders)
        }
    
    def _empty_performance_metrics(self) -> Dict[str, Any]:
        """Return empty performance metrics"""
        return {
            'total_orders': 0,
            'completed_orders': 0,
            'in_progress_orders': 0,
            'completion_rate': 0,
            'on_time_orders': 0,
            'on_time_rate': 0,
            'avg_lead_time_days': 0,
            'avg_delay_days': 0,
            'orders_by_status': {},
            'orders_by_family': {}
        }
    
    def _count_by_status(self, orders: List[Order]) -> Dict[str, int]:
        """Count orders by status"""
        status_count = {}
        for order in orders:
            status_name = order.status.name
            status_count[status_name] = status_count.get(status_name, 0) + 1
        return status_count
    
    def _count_by_family(self, orders: List[Order]) -> Dict[str, int]:
        """Count orders by product family"""
        family_count = {}
        for order in orders:
            family = order.product_family or 'Unknown'
            family_count[family] = family_count.get(family, 0) + 1
        return family_count