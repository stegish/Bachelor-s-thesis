from typing import Dict, Any
from ...domain.interfaces.repository import IOrderRepository, IMachineRepository
from ...domain.interfaces.services import IExportService
from ..services import PhaseAnalyzer, MachineAnalyzer, OrderAnalyzer, BottleneckDetector

class GenerateAnalyticsUseCase:
    def __init__(
        self,
        order_repository: IOrderRepository,
        machine_repository: IMachineRepository,
        export_service: IExportService,
        phase_analyzer: PhaseAnalyzer,
        machine_analyzer: MachineAnalyzer,
        order_analyzer: OrderAnalyzer,
        bottleneck_detector: BottleneckDetector
    ):
        self.order_repository = order_repository
        self.machine_repository = machine_repository
        self.export_service = export_service
        self.phase_analyzer = phase_analyzer
        self.machine_analyzer = machine_analyzer
        self.order_analyzer = order_analyzer
        self.bottleneck_detector = bottleneck_detector
    
    async def execute(self, output_directory: str) -> Dict[str, Any]:
        # 1. Fetch data
        orders = await self.order_repository.get_all()
        machines = await self.machine_repository.get_all()
        
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