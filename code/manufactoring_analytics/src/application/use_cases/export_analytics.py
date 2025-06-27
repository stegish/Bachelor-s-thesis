from typing import Dict, Any, Optional
import os
import zipfile
from datetime import datetime
from ...domain.interfaces import IAnalyticsRepository
from ..dto import ExportAnalyticsRequest, ExportAnalyticsResponse

class ExportAnalyticsUseCase:
    """Use case for exporting analytics data"""
    
    def __init__(
        self,
        analytics_repository: IAnalyticsRepository,
        output_directory: str
    ):
        self.analytics_repository = analytics_repository
        self.output_directory = output_directory
    
    async def execute(self, request: ExportAnalyticsRequest) -> ExportAnalyticsResponse:
        """Export analytics in requested format"""
        try:
            # Get latest analytics result
            latest_result = await self.analytics_repository.get_latest_result()
            
            if not latest_result:
                return ExportAnalyticsResponse(
                    status='error',
                    message='No analytics results found',
                    timestamp=datetime.now(),
                    file_path='',
                    file_size=0,
                    format=request.format
                )
            
            # Export based on format
            if request.format == 'csv':
                file_path = self._get_csv_files()
            elif request.format == 'json':
                file_path = self._export_json(latest_result, request.include_summary)
            else:  # zip
                file_path = self._create_zip_archive()
            
            # Get file size
            file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
            
            return ExportAnalyticsResponse(
                status='success',
                message=f'Analytics exported as {request.format}',
                timestamp=datetime.now(),
                file_path=file_path,
                file_size=file_size,
                format=request.format
            )
            
        except Exception as e:
            return ExportAnalyticsResponse(
                status='error',
                message=f'Export failed: {str(e)}',
                timestamp=datetime.now(),
                file_path='',
                file_size=0,
                format=request.format
            )
    
    def _get_csv_files(self) -> str:
        """Get path to CSV files directory"""
        return self.output_directory
    
    def _export_json(self, result: Any, include_summary: bool) -> str:
        """Export analytics result as JSON"""
        import json
        
        filename = f"analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.output_directory, filename)
        
        export_data = result.to_dict() if hasattr(result, 'to_dict') else {}
        
        if not include_summary:
            export_data.pop('summary', None)
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return filepath
    
    def _create_zip_archive(self) -> str:
        """Create ZIP archive of all analytics files"""
        zip_filename = f"analytics_all_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(self.output_directory, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.output_directory):
                for file in files:
                    if file != zip_filename and not file.endswith('.zip'):
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.output_directory)
                        zipf.write(file_path, arcname)
        
        return zip_path
