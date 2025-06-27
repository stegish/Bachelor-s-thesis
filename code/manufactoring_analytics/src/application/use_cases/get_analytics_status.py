from typing import Dict, Any, Optional
import os
from datetime import datetime
from ...domain.interfaces.repository import IAnalyticsRepository
from ...domain.interfaces.services import ISchedulerService
from ..dto import GetAnalyticsStatusRequest, AnalyticsStatusResponse

class GetAnalyticsStatusUseCase:
    def __init__(
        self,
        analytics_repository: IAnalyticsRepository,
        scheduler_service: ISchedulerService,
        output_directory: str
    ):
        self.analytics_repository = analytics_repository
        self.scheduler_service = scheduler_service
        self.output_directory = output_directory
    
    async def execute(self, request: GetAnalyticsStatusRequest) -> AnalyticsStatusResponse:
        try:
            # Get latest result
            latest_result = await self.analytics_repository.get_latest_result()
            
            # Get available files
            files_available = []
            if os.path.exists(self.output_directory):
                files_available = [f for f in os.listdir(self.output_directory) 
                                 if os.path.isfile(os.path.join(self.output_directory, f))]
            
            # Get scheduler status
            is_running = self.scheduler_service.is_running()
            scheduled_tasks = self.scheduler_service.get_scheduled_tasks()
            
            return AnalyticsStatusResponse(
                status='success',
                message='Analytics status retrieved',
                timestamp=datetime.now(),
                last_run=latest_result.timestamp if latest_result else None,
                next_scheduled_run=scheduled_tasks[0]['next_run'] if scheduled_tasks else None,
                is_running=is_running,
                files_available=files_available,
                history=[] if not request.include_history else []  # Implement history if needed
            )
        except Exception as e:
            return AnalyticsStatusResponse(
                status='error',
                message=f'Failed to get status: {str(e)}',
                timestamp=datetime.now(),
                last_run=None,
                next_scheduled_run=None,
                is_running=False,
                files_available=[],
                history=None
            )