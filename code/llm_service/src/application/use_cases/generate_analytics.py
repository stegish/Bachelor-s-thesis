# src/application/use_cases/generate_analytics.py
from typing import Dict, Any
from ...domain.interfaces import IDataRepository, IExportService
from ..services import PhaseAnalyzer, MachineAnalyzer, OrderAnalyzer, BottleneckDetector

class GenerateAnalyticsUseCase:
    """Use case for generating all analytics"""
    
    def __init__(
        self,
        data_repository: IDataRepository,
        phase_analyzer: PhaseAnalyzer,
        machine_analyzer: MachineAnalyzer,
        order_analyzer: OrderAnalyzer,
        bottleneck_detector: BottleneckDetector,
        export_service: IExportService
    ):
        self.data_repository = data_repository
        self.phase_analyzer = phase_analyzer
        self.machine_analyzer = machine_analyzer
        self.order_analyzer = order_analyzer
        self.bottleneck_detector = bottleneck_detector
        self.export_service = export_service
    
    async def execute(self, output_directory: str) -> Dict[str, Any]:
        """Generate all analytics following SRP"""
        # 1. Fetch data
        orders = await self.data_repository.get_all_orders()
        machines = await self.data_repository.get_all_machines()
        
        # 2. Analyze phases
        phase_metrics = self.phase_analyzer.analyze_phases(orders)
        
        # 3. Analyze machines
        machine_metrics = self.machine_analyzer.analyze_machines(machines, orders)
        
        # 4. Analyze orders
        order_timeline = self.order_analyzer.analyze_timeline(orders)
        
        # 5. Detect bottlenecks
        bottlenecks = self.bottleneck_detector.detect(phase_metrics)
        
        # 6. Export results
        export_result = await self.export_service.export_all({
            'phase_metrics': phase_metrics,
            'machine_metrics': machine_metrics,
            'order_timeline': order_timeline,
            'queue_analysis': bottlenecks['queue_analysis'],
            'operator_performance': bottlenecks['operator_performance']
        }, output_directory)
        
        return {
            'status': 'success',
            'files_generated': export_result['file_count'],
            'summary': export_result['summary']
        }