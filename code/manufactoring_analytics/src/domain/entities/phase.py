from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from ..value_objects import PhaseStatus

@dataclass
class Phase:
    """Phase domain entity"""
    phase_id: str
    name: str
    status: PhaseStatus
    cycle_time: int
    phase_real_time: int = 0
    declared_quantity: int = 0
    operators: List[str] = field(default_factory=list)
    queue_insert_date: Optional[datetime] = None
    queue_real_insert_date: Optional[datetime] = None
    finish_date: Optional[datetime] = None
    real_finish_date: Optional[datetime] = None
    
    @property
    def queue_delay_hours(self) -> Optional[float]:
        """Calculate queue delay in hours"""
        if self.queue_insert_date and self.queue_real_insert_date:
            delta = self.queue_real_insert_date - self.queue_insert_date
            return delta.total_seconds() / 3600
        return None
    
    @property
    def finish_delay_hours(self) -> Optional[float]:
        """Calculate finish delay in hours"""
        if self.finish_date and self.real_finish_date:
            delta = self.real_finish_date - self.finish_date
            return delta.total_seconds() / 3600
        return None
    
    @property
    def actual_duration(self) -> Optional[float]:
        """Calculate actual duration in minutes"""
        if self.queue_real_insert_date and self.real_finish_date:
            delta = self.real_finish_date - self.queue_real_insert_date
            return delta.total_seconds() / 60
        return None
    
    @property
    def planned_duration(self) -> float:
        """Calculate planned duration in minutes"""
        if self.declared_quantity > 0:
            return self.cycle_time * self.declared_quantity
        return self.cycle_time
    
    @property
    def efficiency(self) -> Optional[float]:
        """Calculate phase efficiency percentage"""
        if self.actual_duration and self.actual_duration > 0:
            return (self.cycle_time / self.actual_duration) * 100
        return None