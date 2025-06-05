import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pymongo import MongoClient
from typing import List, Dict, Any
import csv
import json
from collections import defaultdict

class ManufacturingAnalytics:
    def __init__(self, mongo_uri: str, database_name: str):
        """Initialize the analytics service with MongoDB connection"""

        self.client = MongoClient(mongo_uri)
        self.db = self.client[database_name]
        self.orders_collection = self.db['NewOrder']
        self.machines_collection = self.db['macchinari']
        
    def extract_phase_metrics(self, orders: List[Dict]) -> pd.DataFrame:
        """Extract detailed phase-level metrics from orders"""
        phase_data = []
        
        for order in orders:
            order_id = order.get('orderId', '')
            order_status = order.get('orderStatus', {}).get('$numberInt', 0)
            order_quantity = order.get('quantity', {}).get('$numberInt', 0)
            
            phases = order.get('Phases', [])
            
            for phase in phases:
                phase_record = {
                    'order_id': order_id,
                    'order_status': int(order_status),
                    'order_quantity': int(order_quantity),
                    'phase_id': phase.get('phaseId', ''),
                    'phase_name': phase.get('phaseName', ''),
                    'phase_status': int(phase.get('phaseStatus', {}).get('$numberInt', 0)),
                    'cycle_time': int(phase.get('cycleTime', {}).get('$numberInt', 0)),
                    'phase_real_time': int(phase.get('phaseRealTime', {}).get('$numberInt', 0)),
                    'declared_quantity': int(phase.get('declaredQuantity', {}).get('$numberInt', 0)) if phase.get('declaredQuantity') else 0,
                    'operators': ','.join(phase.get('operators', [])),
                    'operator_count': len(phase.get('operators', [])),
                }
                
                # Extract dates
                queue_insert = phase.get('queueInsertDate', {}).get('$date', {}).get('$numberLong')
                queue_real_insert = phase.get('queueRealInsertDate', {}).get('$date', {}).get('$numberLong')
                finish_date = phase.get('finishDate', {}).get('$date', {}).get('$numberLong')
                real_finish = phase.get('realFinishDate', {}).get('$date', {}).get('$numberLong')
                
                phase_record['queue_insert_date'] = datetime.fromtimestamp(int(queue_insert)/1000) if queue_insert else None
                phase_record['queue_real_insert_date'] = datetime.fromtimestamp(int(queue_real_insert)/1000) if queue_real_insert else None
                phase_record['planned_finish_date'] = datetime.fromtimestamp(int(finish_date)/1000) if finish_date else None
                phase_record['real_finish_date'] = datetime.fromtimestamp(int(real_finish)/1000) if real_finish else None
                
                # Calculate delays and efficiency metrics
                if phase_record['queue_insert_date'] and phase_record['queue_real_insert_date']:
                    phase_record['queue_delay_hours'] = (phase_record['queue_real_insert_date'] - 
                                                        phase_record['queue_insert_date']).total_seconds() / 3600
                else:
                    phase_record['queue_delay_hours'] = None
                
                if phase_record['planned_finish_date'] and phase_record['real_finish_date']:
                    phase_record['finish_delay_hours'] = (phase_record['real_finish_date'] - 
                                                         phase_record['planned_finish_date']).total_seconds() / 3600
                else:
                    phase_record['finish_delay_hours'] = None
                
                # Calculate actual vs planned cycle time
                if phase_record['queue_real_insert_date'] and phase_record['real_finish_date']:
                    phase_record['actual_duration_minutes'] = (phase_record['real_finish_date'] - 
                                                              phase_record['queue_real_insert_date']).total_seconds() / 60
                else:
                    phase_record['actual_duration_minutes'] = None
                
                phase_record['planned_duration_minutes'] = phase_record['cycle_time'] * phase_record['declared_quantity'] if phase_record['declared_quantity'] > 0 else phase_record['cycle_time']
                
                phase_data.append(phase_record)
        
        return pd.DataFrame(phase_data)
    
    def calculate_machine_metrics(self, phase_df: pd.DataFrame, machines: List[Dict]) -> pd.DataFrame:
        """Calculate machine-level metrics including utilization and queue statistics"""
        machine_metrics = []
        
        for machine in machines:
            machine_name = machine.get('name', '')
            is_active = machine.get('macchinarioActive', False)
            queue_target_time = int(machine.get('queueTargetTime', {}).get('$numberInt', 0))
            current_queue_length = len(machine.get('tablet', []))
            
            # Filter phases for this machine
            if 'phase_name' in phase_df.columns:
                machine_phases = phase_df[phase_df['phase_name'] == machine_name]
            else:
                machine_phases = pd.DataFrame()
            
            if len(machine_phases) > 0:
                metrics = {
                    'machine_name': machine_name,
                    'is_active': is_active,
                    'queue_target_time': queue_target_time,
                    'current_queue_length': current_queue_length,
                    'total_phases_processed': len(machine_phases),
                    'completed_phases': len(machine_phases[machine_phases['phase_status'] == 4]),
                    'in_progress_phases': len(machine_phases[machine_phases['phase_status'].isin([1, 2, 3])]),
                    'avg_cycle_time': machine_phases['cycle_time'].mean(),
                    'avg_actual_duration': machine_phases['actual_duration_minutes'].mean(),
                    'avg_queue_delay': machine_phases['queue_delay_hours'].mean(),
                    'avg_finish_delay': machine_phases['finish_delay_hours'].mean(),
                    'total_quantity_processed': machine_phases['declared_quantity'].sum(),
                    'unique_operators': len(set(','.join(machine_phases['operators'].fillna('')).split(','))),
                }
                
                # Calculate efficiency
                if metrics['avg_cycle_time'] > 0 and not pd.isna(metrics['avg_actual_duration']):
                    metrics['efficiency_percentage'] = (metrics['avg_cycle_time'] / metrics['avg_actual_duration']) * 100
                else:
                    metrics['efficiency_percentage'] = None
                
                # Calculate utilization (assuming 8 hour work day)
                if len(machine_phases[machine_phases['real_finish_date'].notna()]) > 0:
                    date_range = (machine_phases['real_finish_date'].max() - machine_phases['queue_real_insert_date'].min())
                    working_days = date_range.days
                    if working_days > 0:
                        total_working_minutes = working_days * 8 * 60
                        total_actual_minutes = machine_phases['actual_duration_minutes'].sum()
                        metrics['utilization_percentage'] = (total_actual_minutes / total_working_minutes) * 100
                    else:
                        metrics['utilization_percentage'] = None
                else:
                    metrics['utilization_percentage'] = None
                
                machine_metrics.append(metrics)
        
        return pd.DataFrame(machine_metrics)
    
    def generate_order_timeline(self, orders: List[Dict]) -> pd.DataFrame:
        """Generate order timeline data for tracking order progress"""
        timeline_data = []
        
        for order in orders:
            order_id = order.get('orderId', '')
            order_insert = order.get('orderInsertDate', {}).get('$date', {}).get('$numberLong')
            order_start = order.get('orderStartDate', {}).get('$date', {}).get('$numberLong')
            order_deadline = order.get('orderDeadline', {}).get('$date', {}).get('$numberLong')
            real_finish = order.get('realOrderFinishDate', {}).get('$date', {}).get('$numberLong')
            
            record = {
                'order_id': order_id,
                'article_code': order.get('codiceArticolo', ''),
                'product_family': order.get('famigliaDiProdotto', ''),
                'quantity': int(order.get('quantity', {}).get('$numberInt', 0)),
                'priority': int(order.get('priority', {}).get('$numberInt', 0)),
                'order_status': int(order.get('orderStatus', {}).get('$numberInt', 0)),
                'insert_date': datetime.fromtimestamp(int(order_insert)/1000) if order_insert else None,
                'start_date': datetime.fromtimestamp(int(order_start)/1000) if order_start else None,
                'deadline': datetime.fromtimestamp(int(order_deadline)/1000) if order_deadline else None,
                'real_finish_date': datetime.fromtimestamp(int(real_finish)/1000) if real_finish else None,
            }
            
            # Calculate lead time and delays
            if record['insert_date'] and record['real_finish_date']:
                record['lead_time_days'] = (record['real_finish_date'] - record['insert_date']).days
            else:
                record['lead_time_days'] = None
                
            if record['deadline'] and record['real_finish_date']:
                record['delay_days'] = (record['real_finish_date'] - record['deadline']).days
                record['on_time'] = record['delay_days'] <= 0
            else:
                record['delay_days'] = None
                record['on_time'] = None
            
            timeline_data.append(record)
        
        return pd.DataFrame(timeline_data)
    
    def generate_queue_analysis(self, phase_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze queue patterns and bottlenecks"""
        if phase_df.empty or 'phase_name' not in phase_df.columns:
            return pd.DataFrame(columns=[
                'phase_name', 'avg_queue_delay', 'queue_delay_std',
                'max_queue_delay', 'total_jobs', 'total_quantity',
                'is_bottleneck']
            )

        # Group by machine and calculate queue metrics
        queue_metrics = phase_df.groupby('phase_name').agg({
            'queue_delay_hours': ['mean', 'std', 'max'],
            'phase_id': 'count',
            'declared_quantity': 'sum'
        }).round(2)
        
        queue_metrics.columns = ['avg_queue_delay', 'queue_delay_std', 'max_queue_delay', 
                                'total_jobs', 'total_quantity']
        queue_metrics = queue_metrics.reset_index()
        
        # Identify bottlenecks (machines with high average queue delay)
        queue_metrics['is_bottleneck'] = queue_metrics['avg_queue_delay'] > queue_metrics['avg_queue_delay'].mean() + queue_metrics['avg_queue_delay'].std()
        
        return queue_metrics
    
    def generate_operator_performance(self, phase_df: pd.DataFrame) -> pd.DataFrame:
        """Analyze operator performance metrics"""
        operator_data = []
        
        # Split operator strings and create individual records
        for _, row in phase_df.iterrows():
            if 'operators' in row and row['operators']:
                operators = row['operators'].split(',')
                for operator in operators:
                    operator = operator.strip()
                    if operator:
                        operator_data.append({
                            'operator': operator,
                            'phase_name': row['phase_name'],
                            'cycle_time': row['cycle_time'],
                            'actual_duration': row['actual_duration_minutes'],
                            'declared_quantity': row['declared_quantity'],
                            'phase_status': row['phase_status']
                        })
        
        operator_df = pd.DataFrame(operator_data)
        
        if len(operator_df) > 0:
            # Calculate operator metrics
            operator_metrics = operator_df.groupby('operator').agg({
                'phase_name': 'count',
                'cycle_time': 'mean',
                'actual_duration': 'mean',
                'declared_quantity': 'sum'
            }).round(2)
            
            operator_metrics.columns = ['total_phases', 'avg_cycle_time', 'avg_actual_duration', 'total_quantity']
            operator_metrics['efficiency'] = (operator_metrics['avg_cycle_time'] / operator_metrics['avg_actual_duration'] * 100).round(2)
            operator_metrics = operator_metrics.reset_index()
        else:
            operator_metrics = pd.DataFrame()
        
        return operator_metrics
    
    def export_to_csv(self, output_dir: str = './analytics_output'):
        """Export all analytics to CSV files"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Fetch data from MongoDB
        orders = list(self.orders_collection.find())
        machines = list(self.machines_collection.find())
        
        # Generate analytics
        print("Extracting phase metrics...")
        phase_df = self.extract_phase_metrics(orders)
        phase_df.to_csv(f'{output_dir}/phase_metrics.csv', index=False)
        
        print("Calculating machine metrics...")
        machine_metrics = self.calculate_machine_metrics(phase_df, machines)
        machine_metrics.to_csv(f'{output_dir}/machine_metrics.csv', index=False)
        
        print("Generating order timeline...")
        order_timeline = self.generate_order_timeline(orders)
        order_timeline.to_csv(f'{output_dir}/order_timeline.csv', index=False)
        
        print("Analyzing queue patterns...")
        queue_analysis = self.generate_queue_analysis(phase_df)
        queue_analysis.to_csv(f'{output_dir}/queue_analysis.csv', index=False)
        
        print("Calculating operator performance...")
        operator_performance = self.generate_operator_performance(phase_df)
        operator_performance.to_csv(f'{output_dir}/operator_performance.csv', index=False)
        
        # Generate summary statistics
        summary = {
            'total_orders': len(orders),
            'completed_orders': len([o for o in orders if o.get('orderStatus', {}).get('$numberInt') == '4']),
            'active_machines': len([m for m in machines if m.get('macchinarioActive', False)]),
            'total_machines': len(machines),
            'avg_order_lead_time': order_timeline['lead_time_days'].mean() if 'lead_time_days' in order_timeline else None,
            'on_time_delivery_rate': (
                order_timeline['on_time'].sum() / len(order_timeline[order_timeline['on_time'].notna()]) * 100
            ) if 'on_time' in order_timeline and len(order_timeline[order_timeline['on_time'].notna()]) > 0 else 0,
            'avg_machine_utilization': machine_metrics['utilization_percentage'].mean() if 'utilization_percentage' in machine_metrics else None,
            'avg_machine_efficiency': machine_metrics['efficiency_percentage'].mean() if 'efficiency_percentage' in machine_metrics else None,
            'total_operators': len(operator_performance) if len(operator_performance) > 0 else 0,
            'bottleneck_machines': (
                queue_analysis.loc[queue_analysis['is_bottleneck'], 'phase_name'].tolist()
                if 'phase_name' in queue_analysis.columns and 'is_bottleneck' in queue_analysis.columns
                else []
            )
        }
        
        with open(f'{output_dir}/summary_statistics.json', 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\nAnalytics exported to {output_dir}/")
        print("\nGenerated files:")
        print("- phase_metrics.csv: Detailed phase-level data")
        print("- machine_metrics.csv: Machine utilization and efficiency")
        print("- order_timeline.csv: Order progress and delays")
        print("- queue_analysis.csv: Queue patterns and bottlenecks")
        print("- operator_performance.csv: Operator efficiency metrics")
        print("- summary_statistics.json: Overall KPIs")
        
        return summary


# Example usage
if __name__ == "__main__":
    # Configure your MongoDB connection
    MONGO_URI = "mongodb://localhost:27017/"  # Update with your MongoDB URI
    DATABASE_NAME = "your_database_name"  # Update with your database name
    
    # Initialize the analytics service
    analytics = ManufacturingAnalytics(MONGO_URI, DATABASE_NAME)
    
    # Generate all analytics and export to CSV
    summary = analytics.export_to_csv()
    
    print("\nSummary Statistics:")
    for key, value in summary.items():
        print(f"{key}: {value}")