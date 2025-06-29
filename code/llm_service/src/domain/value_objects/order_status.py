from enum import IntEnum

class OrderStatus(IntEnum):
    """Order status value object"""
    PENDING = 0
    IN_PROGRESS = 1
    ON_HOLD = 2
    QUALITY_CHECK = 3
    COMPLETED = 4
    CANCELLED = 5
    
    @classmethod
    def from_value(cls, value: int) -> 'OrderStatus':
        """Create from integer value"""
        try:
            return cls(value)
        except ValueError:
            return cls.PENDING