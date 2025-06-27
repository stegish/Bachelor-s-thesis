# src/domain/value_objects/date_range.py
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

@dataclass(frozen=True)
class DateRange:
    """Date range value object - immutable"""
    start_date: datetime
    end_date: datetime
    
    def __post_init__(self):
        """Validate date range"""
        if self.start_date > self.end_date:
            raise ValueError("Start date must be before end date")
    
    @property
    def duration_days(self) -> int:
        """Get duration in days"""
        return (self.end_date - self.start_date).days
    
    @property
    def working_days(self) -> int:
        """Get number of working days (excluding weekends)"""
        count = 0
        current = self.start_date
        while current <= self.end_date:
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                count += 1
            current += timedelta(days=1)
        return count
    
    def contains(self, date: datetime) -> bool:
        """Check if date is within range"""
        return self.start_date <= date <= self.end_date