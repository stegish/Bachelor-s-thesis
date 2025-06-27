from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import Dict, Any, List, Callable
from datetime import datetime
import asyncio
import logging
from ...domain.interfaces import ISchedulerService

logger = logging.getLogger(__name__)

class Scheduler(ISchedulerService):
    """APScheduler implementation of scheduler service"""
    
    def __init__(self):
        self._scheduler = AsyncIOScheduler()
        self._jobs: Dict[str, Any] = {}
    
    def schedule_task(self, task_func: Callable, interval_minutes: int) -> str:
        """Schedule a recurring task"""
        try:
            job = self._scheduler.add_job(
                task_func,
                trigger=IntervalTrigger(minutes=interval_minutes),
                id=f"task_{datetime.now().timestamp()}",
                name=task_func.__name__,
                replace_existing=True
            )
            
            self._jobs[job.id] = {
                'name': job.name,
                'interval': interval_minutes,
                'next_run': None  # Will be set when scheduler starts
            }
            
            logger.info(f"Scheduled task {job.name} every {interval_minutes} minutes")
            return job.id
        except Exception as e:
            logger.error(f"Error scheduling task: {e}")
            raise
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task"""
        try:
            self._scheduler.remove_job(task_id)
            self._jobs.pop(task_id, None)
            logger.info(f"Cancelled task {task_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling task {task_id}: {e}")
            return False
    
    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Get list of scheduled tasks"""
        tasks = []
        for job in self._scheduler.get_jobs():
            tasks.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return tasks
    
    def start(self) -> None:
        """Start the scheduler"""
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("Scheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler"""
        if self._scheduler.running:
            self._scheduler.shutdown(wait=True)
            logger.info("Scheduler stopped")
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self._scheduler.running