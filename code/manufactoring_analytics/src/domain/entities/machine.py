from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Machine:
    """Machine domain entity"""
    name: str
    is_active: bool
    queue_target_time: int
    current_queue: List[Dict[str, Any]] = field(default_factory=list)
    
    @property
    def queue_length(self) -> int:
        """Get current queue length"""
        return len(self.current_queue)
    
    @property
    def is_available(self) -> bool:
        """Check if machine is available for new jobs"""
        return self.is_active and self.queue_length < 100  # Max queue size
    
    def add_to_queue(self, job: Dict[str, Any]) -> None:
        """Add job to queue"""
        if not self.is_available:
            raise ValueError(f"Machine {self.name} is not available")
        self.current_queue.append(job)
    
    def remove_from_queue(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Remove job from queue"""
        for i, job in enumerate(self.current_queue):
            if job.get('id') == job_id:
                return self.current_queue.pop(i)
        return None