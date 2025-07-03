from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any
from datetime import datetime
import json
import os
from glob import glob
import logging
from ....infrastructure.config import Container
from ....application.dto import GenerateAnalyticsRequest, GenerateAnalyticsResponse
from ....application.use_cases import GenerateAnalyticsUseCase
from dependency_injector.wiring import inject, Provide

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/run")
@inject
async def generate_analytics(
    background_tasks: BackgroundTasks,
    force: bool = False,
    use_case: GenerateAnalyticsUseCase = Depends(Provide[Container.generate_analytics_use_case])
) -> GenerateAnalyticsResponse:
    """Generate manufacturing analytics"""
    try:
        request = GenerateAnalyticsRequest(
            output_directory="./analytics_output",
            force_regenerate=force
        )
        
        # Run analytics generation
        result = await use_case.execute(request.output_directory)
        
        return GenerateAnalyticsResponse(
            status="success",
            message="Analytics generation completed",
            timestamp=datetime.now(),
            files_generated=result['files_generated'],
            summary=result['summary']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
@inject
async def get_analytics_status(
    use_case = Depends(Provide[Container.get_analytics_status_use_case])
) -> Dict[str, Any]:
    """Get current analytics generation status"""
    from ....application.dto import GetAnalyticsStatusRequest
    
    request = GetAnalyticsStatusRequest(include_history=True, limit=10)
    result = await use_case.execute(request)
    
    return result.dict()

@router.get("/summary")
@inject
async def get_analytics_summary(
    analytics_repo = Depends(Provide[Container.analytics_repository])
) -> Dict[str, Any]:
    """Get latest analytics summary"""
    # Prima prova il database
    latest = await analytics_repo.get_latest_result()
    
    if latest:
        return latest.to_dict()
    
    # Se non c'è nel database, leggi dal file JSON più recente
    output_dir = './analytics_output'  # O usa la configurazione dal container
    
    # Cerca tutti i file summary_statistics_*.json
    summary_files = glob(os.path.join(output_dir, 'summary_statistics_*.json'))
    
    if not summary_files:
        raise HTTPException(status_code=404, detail="No analytics results found")
    
    # Ordina per data nel nome del file e prendi il più recente
    latest_file = max(summary_files, key=lambda x: os.path.basename(x))
    
    try:
        with open(latest_file, 'r') as f:
            summary_data = json.load(f)
        
        # Converti in formato AnalyticsSummary compatibile
        return {
            'timestamp': datetime.now().isoformat(),
            'total_orders': summary_data.get('total_orders', 0),
            'completed_orders': summary_data.get('completed_orders', 0),
            'active_machines': summary_data.get('active_machines', 0),
            'total_machines': summary_data.get('total_machines', 0),
            'avg_order_lead_time': summary_data.get('avg_lead_time', 0.0),
            'on_time_delivery_rate': summary_data.get('on_time_rate', 0.0),
            'avg_machine_utilization': summary_data.get('avg_utilization', 0.0),
            'avg_machine_efficiency': summary_data.get('avg_efficiency', 0.0),
            'total_operators': summary_data.get('total_operators', 0),
            'bottleneck_machines': summary_data.get('bottleneck_machines', []),
            'files_generated': {
                'machine_metrics.csv': True,
                'order_timeline.csv': True,
                'phase_metrics.csv': True,
                'queue_analysis.csv': True,
                'operator_performance.csv': True
            }
        }
    except Exception as e:
        logger.error(f"Error reading summary file: {e}")
        raise HTTPException(status_code=500, detail="Error reading analytics summary")