from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd

class IExportService(ABC):
    @abstractmethod
    async def export_all(self, data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def export_to_csv(self, data: Dict[str, pd.DataFrame], output_dir: str) -> Dict[str, str]:
        pass
    
    @abstractmethod
    async def export_to_json(self, data: Dict[str, Any], output_dir: str) -> str:
        pass

class ISchedulerService(ABC):
    @abstractmethod
    def schedule_task(self, task_func: callable, interval_minutes: int) -> str:
        pass
    
    @abstractmethod
    def cancel_task(self, task_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def start(self) -> None:
        pass
    
    @abstractmethod
    def stop(self) -> None:
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        pass