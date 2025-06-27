# src/domain/entities/order.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from ..value_objects import OrderStatus

@dataclass
class Order:
    """Order domain entity"""
    order_id: str
    article_code: str
    product_family: str
    quantity: int
    priority: int
    status: OrderStatus
    insert_date: datetime
    start_date: Optional[datetime]
    deadline: Optional[datetime]
    finish_date: Optional[datetime]
    phases: List['Phase']
    
    @property
    def lead_time_days(self) -> Optional[int]:
        """Calculate lead time in days"""
        if self.insert_date and self.finish_date:
            return (self.finish_date - self.insert_date).days
        return None
    
    @property
    def is_delayed(self) -> bool:
        """Check if order is delayed"""
        if self.deadline and self.finish_date:
            return self.finish_date > self.deadline
        return False