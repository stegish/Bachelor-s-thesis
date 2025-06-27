from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..entities import Order, Machine, AnalyticsResult

class IDataRepository(ABC):
    """Combined data repository interface"""
    
    @abstractmethod
    async def get_all_orders(self, limit: Optional[int] = None) -> List[Order]:
        pass
    
    @abstractmethod
    async def get_all_machines(self) -> List[Machine]:
        pass

class IOrderRepository(ABC):
    @abstractmethod
    async def get_all(self, limit: Optional[int] = None) -> List[Order]:
        pass
    
    @abstractmethod
    async def get_by_id(self, order_id: str) -> Optional[Order]:
        pass
    
    @abstractmethod
    async def get_by_status(self, status: int) -> List[Order]:
        pass
    
    @abstractmethod
    async def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Order]:
        pass

class IMachineRepository(ABC):
    @abstractmethod
    async def get_all(self) -> List[Machine]:
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Machine]:
        pass
    
    @abstractmethod
    async def get_active_machines(self) -> List[Machine]:
        pass

class IAnalyticsRepository(ABC):
    @abstractmethod
    async def save_result(self, result: AnalyticsResult) -> None:
        pass
    
    @abstractmethod
    async def get_latest_result(self) -> Optional[AnalyticsResult]:
        pass
    
    @abstractmethod
    async def get_results_by_date_range(self, start_date: datetime, end_date: datetime) -> List[AnalyticsResult]:
        pass