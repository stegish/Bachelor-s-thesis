from typing import Dict, Any, List
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class BottleneckDetector:
    """Service for detecting production bottlenecks following SRP"""
    
    def detect(self, phase_df: pd.DataFrame) -> Dict[str, Any]:
        """Detect bottlenecks in production"""
        if phase_df.empty:
            logger.info("No phase data available for bottleneck detection")
            return {
                'queue_analysis': pd.DataFrame(),
                'operator_performance': pd.DataFrame(),
                'bottleneck_machines': []
            }
        
        try:
            queue_analysis = self._analyze_queues(phase_df)
            operator_performance = self._analyze_operators(phase_df)
            
            return {
                'queue_analysis': queue_analysis,
                'operator_performance': operator_performance,
                'bottleneck_machines': self._identify_bottlenecks(queue_analysis)
            }
        except Exception as e:
            logger.error(f"Error in bottleneck detection: {e}")
            return {
                'queue_analysis': pd.DataFrame(),
                'operator_performance': pd.DataFrame(),
                'bottleneck_machines': []
            }
    
    def _analyze_queues(self, phase_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze queue patterns"""
        try:
            # Check which columns exist
            available_columns = phase_df.columns.tolist()
            
            # Define aggregation based on available columns
            agg_dict = {}
            
            if 'queue_delay_hours' in available_columns:
                agg_dict['queue_delay_hours'] = ['mean', 'std', 'max']
            
            if 'phase_id' in available_columns:
                agg_dict['phase_id'] = 'count'
            
            if 'declared_quantity' in available_columns:
                agg_dict['declared_quantity'] = 'sum'
            
            # If we don't have any columns to aggregate, return empty
            if not agg_dict or 'phase_name' not in available_columns:
                logger.warning("Insufficient columns for queue analysis")
                return pd.DataFrame()
            
            queue_metrics = phase_df.groupby('phase_name').agg(agg_dict).round(2)
            
            # Flatten column names
            queue_metrics.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col 
                                    for col in queue_metrics.columns]
            
            # Rename columns based on what exists
            rename_dict = {}
            if 'queue_delay_hours_mean' in queue_metrics.columns:
                rename_dict['queue_delay_hours_mean'] = 'avg_queue_delay'
                rename_dict['queue_delay_hours_std'] = 'queue_delay_std'
                rename_dict['queue_delay_hours_max'] = 'max_queue_delay'
            
            if 'phase_id_count' in queue_metrics.columns:
                rename_dict['phase_id_count'] = 'total_jobs'
            
            if 'declared_quantity_sum' in queue_metrics.columns:
                rename_dict['declared_quantity_sum'] = 'total_quantity'
            
            queue_metrics = queue_metrics.rename(columns=rename_dict)
            queue_metrics = queue_metrics.reset_index()
            
            # Mark bottlenecks only if we have queue delay data
            if 'avg_queue_delay' in queue_metrics.columns:
                global_mean = queue_metrics['avg_queue_delay'].mean()
                global_std = queue_metrics['avg_queue_delay'].std()
                threshold = global_mean + (global_std if not pd.isna(global_std) else 0)
                
                queue_metrics['is_bottleneck'] = queue_metrics['avg_queue_delay'] > threshold
            else:
                queue_metrics['is_bottleneck'] = False
            
            return queue_metrics
            
        except Exception as e:
            logger.error(f"Error analyzing queues: {e}")
            return pd.DataFrame()
    
    def _analyze_operators(self, phase_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze operator performance"""
        try:
            # Check if required columns exist
            if 'operators' not in phase_df.columns:
                logger.warning("No operator data available")
                return pd.DataFrame()
            
            operator_data = []
            
            for _, row in phase_df.iterrows():
                operators = row.get('operators', '')
                if operators:
                    for operator in str(operators).split(','):
                        operator = operator.strip()
                        if operator:
                            record = {
                                'operator': operator,
                                'phase_name': row.get('phase_name', 'Unknown')
                            }
                            
                            # Add optional fields if they exist
                            if 'cycle_time' in row:
                                record['cycle_time'] = row['cycle_time']
                            if 'actual_duration' in row:
                                record['actual_duration'] = row.get('actual_duration', 0)
                            if 'declared_quantity' in row:
                                record['declared_quantity'] = row.get('declared_quantity', 0)
                            
                            operator_data.append(record)
            
            if not operator_data:
                return pd.DataFrame()
            
            operator_df = pd.DataFrame(operator_data)
            
            # Build aggregation dict based on available columns
            agg_dict = {'phase_name': 'count'}
            if 'cycle_time' in operator_df.columns:
                agg_dict['cycle_time'] = 'mean'
            if 'actual_duration' in operator_df.columns:
                agg_dict['actual_duration'] = 'mean'
            if 'declared_quantity' in operator_df.columns:
                agg_dict['declared_quantity'] = 'sum'
            
            operator_metrics = operator_df.groupby('operator').agg(agg_dict).round(2)
            
            # Rename columns
            rename_dict = {'phase_name': 'total_phases'}
            if 'cycle_time' in operator_metrics.columns:
                rename_dict['cycle_time'] = 'avg_cycle_time'
            if 'actual_duration' in operator_metrics.columns:
                rename_dict['actual_duration'] = 'avg_actual_duration'
            if 'declared_quantity' in operator_metrics.columns:
                rename_dict['declared_quantity'] = 'total_quantity'
            
            operator_metrics = operator_metrics.rename(columns=rename_dict)
            
            # Calculate efficiency only if we have both cycle time and actual duration
            if 'avg_cycle_time' in operator_metrics.columns and 'avg_actual_duration' in operator_metrics.columns:
                mask = operator_metrics['avg_actual_duration'] > 0
                operator_metrics.loc[mask, 'efficiency'] = (
                    operator_metrics.loc[mask, 'avg_cycle_time'] / 
                    operator_metrics.loc[mask, 'avg_actual_duration'] * 100
                ).round(2)
                operator_metrics.loc[~mask, 'efficiency'] = None
            
            return operator_metrics.reset_index()
            
        except Exception as e:
            logger.error(f"Error analyzing operators: {e}")
            return pd.DataFrame()
    
    def _identify_bottlenecks(self, queue_analysis: pd.DataFrame) -> List[str]:
        """Identify bottleneck machines"""
        try:
            if queue_analysis.empty or 'is_bottleneck' not in queue_analysis.columns:
                return []
            
            bottlenecks = queue_analysis[queue_analysis['is_bottleneck'] == True]
            
            if 'phase_name' in bottlenecks.columns:
                return bottlenecks['phase_name'].tolist()
            
            return []
            
        except Exception as e:
            logger.error(f"Error identifying bottlenecks: {e}")
            return []