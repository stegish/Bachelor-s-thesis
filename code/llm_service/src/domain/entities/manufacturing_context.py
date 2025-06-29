from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class ManufacturingContext:
    """Manufacturing context domain entity"""
    orders_summary: Dict[str, Any]
    machines_summary: Dict[str, Any]
    current_bottlenecks: List[str]
    recent_metrics: Dict[str, float]
    alerts: List[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'orders_summary': self.orders_summary,
            'machines_summary': self.machines_summary,
            'current_bottlenecks': self.current_bottlenecks,
            'recent_metrics': self.recent_metrics,
            'alerts': self.alerts or []
        }
