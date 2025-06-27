import os
import pandas as pd
import json
import zipfile
from typing import Dict, Any, List
from datetime import datetime
from ....domain.interfaces import IExportService
import logging

logger = logging.getLogger(__name__)

class CSVExporter(IExportService):
    """CSV export service implementation"""
    
    async def export_to_csv(self, data: Dict[str, pd.DataFrame], output_dir: str) -> Dict[str, str]:
        """Export dataframes to CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        files_created = {}
        
        try:
            for name, df in data.items():
                if isinstance(df, pd.DataFrame):
                    filename = f"{name}.csv"
                    filepath = os.path.join(output_dir, filename)
                    df.to_csv(filepath, index=False)
                    files_created[name] = filepath
                    logger.info(f"Exported {name} to {filepath}")
            
            return files_created
        except Exception as e:
            logger.error(f"Error exporting CSV files: {e}")
            raise
    
    async def export_to_json(self, data: Dict[str, Any], output_dir: str) -> str:
        """Export data to JSON file"""
        os.makedirs(output_dir, exist_ok=True)
        
        try:
            filename = f"summary_statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(output_dir, filename)
            
            # Convert pandas DataFrames to dict if present
            export_data = {}
            for key, value in data.items():
                if isinstance(value, pd.DataFrame):
                    export_data[key] = value.to_dict(orient='records')
                else:
                    export_data[key] = value
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Exported JSON to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error exporting JSON file: {e}")
            raise
    
    async def export_all(self, data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """Export all analytics data"""
        # Separate DataFrames from other data
        dataframes = {}
        summary_data = {}
        
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                dataframes[key] = value
            else:
                summary_data[key] = value
        
        # Export CSVs
        csv_files = await self.export_to_csv(dataframes, output_dir)
        
        # Generate summary
        summary = self._generate_summary(dataframes)
        summary_data.update(summary)
        
        # Export summary JSON
        json_file = await self.export_to_json(summary_data, output_dir)
        
        return {
            'file_count': len(csv_files) + 1,
            'csv_files': csv_files,
            'json_file': json_file,
            'summary': summary
        }
    
    def _generate_summary(self, dataframes: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Generate summary statistics"""
        summary = {}
        
        # Extract key metrics from dataframes
        if 'order_timeline' in dataframes and not dataframes['order_timeline'].empty:
            df = dataframes['order_timeline']
            summary['total_orders'] = len(df)
            if 'order_status' in df.columns:
                summary['completed_orders'] = len(df[df['order_status'] == 4])
            else:
                summary['completed_orders'] = 0
            summary['avg_lead_time'] = df['lead_time_days'].mean() if 'lead_time_days' in df.columns else 0
            summary['on_time_rate'] = (
                df['on_time'].sum() / len(df[df['on_time'].notna()]) * 100
                if 'on_time' in df.columns and len(df[df['on_time'].notna()]) > 0
                else 0
            )
        else:
            summary['total_orders'] = 0
            summary['completed_orders'] = 0
            summary['avg_lead_time'] = 0
            summary['on_time_rate'] = 0
        
        if 'machine_metrics' in dataframes and not dataframes['machine_metrics'].empty:
            df = dataframes['machine_metrics']
            summary['total_machines'] = len(df)
            summary['active_machines'] = len(df[df['is_active'] == True]) if 'is_active' in df.columns else 0
            summary['avg_utilization'] = df['utilization_percentage'].mean() if 'utilization_percentage' in df.columns else 0
            summary['avg_efficiency'] = df['efficiency_percentage'].mean() if 'efficiency_percentage' in df.columns else 0
        else:
            summary['total_machines'] = 0
            summary['active_machines'] = 0
            summary['avg_utilization'] = 0
            summary['avg_efficiency'] = 0
        
        if 'queue_analysis' in dataframes and not dataframes['queue_analysis'].empty:
            df = dataframes['queue_analysis']
            if 'is_bottleneck' in df.columns and 'phase_name' in df.columns:
                summary['bottleneck_machines'] = df[df['is_bottleneck'] == True]['phase_name'].tolist()
            else:
                summary['bottleneck_machines'] = []
        else:
            summary['bottleneck_machines'] = []
        
        if 'operator_performance' in dataframes:
            summary['total_operators'] = len(dataframes['operator_performance'])
        else:
            summary['total_operators'] = 0
        
        return summary