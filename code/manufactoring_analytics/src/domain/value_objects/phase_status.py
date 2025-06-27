from enum import IntEnum

class PhaseStatus(IntEnum):
    """Phase status value object"""
    QUEUED = 0
    IN_PROGRESS = 1
    PAUSED = 2
    QUALITY_CHECK = 3
    COMPLETED = 4
    FAILED = 5
    
    @classmethod
    def from_value(cls, value: int) -> 'PhaseStatus':
        """Create from integer value"""
        try:
            return cls(value)
        except ValueError:
            return cls.QUEUED
