from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from ..value_objects import OrderStatus
from .phase import Phase, PhaseStatus  # Add PhaseStatus import


@dataclass
class Order:
    """Order domain entity"""
    order_id: str
    article_code: str
    product_family: str
    quantity: int
    priority: int
    status: OrderStatus
    phases: List[Phase] = field(default_factory=list)
    insert_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None
    real_finish_date: Optional[datetime] = None
    
    @property
    def lead_time_days(self) -> Optional[int]:
        """Calculate lead time in days"""
        if self.insert_date and self.real_finish_date:
            return (self.real_finish_date - self.insert_date).days
        return None
    
    @property
    def delay_days(self) -> Optional[int]:
        """Calculate delay in days"""
        if self.deadline and self.real_finish_date:
            return (self.real_finish_date - self.deadline).days
        return None
    
    @property
    def is_on_time(self) -> Optional[bool]:
        """Check if order was delivered on time"""
        if self.delay_days is not None:
            return self.delay_days <= 0
        return None
    
    @property
    def is_completed(self) -> bool:
        """Check if order is completed"""
        return self.status == OrderStatus.COMPLETED
    
    @property
    def total_phases(self) -> int:
        """Get total number of phases"""
        return len(self.phases)
    
    @property
    def completed_phases(self) -> int:
        """Get number of completed phases"""
        return sum(1 for phase in self.phases if phase.status == PhaseStatus.COMPLETED)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate order progress percentage"""
        if self.total_phases == 0:
            return 0.0
        return (self.completed_phases / self.total_phases) * 100