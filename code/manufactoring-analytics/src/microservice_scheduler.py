import schedule
import time
import shutil
from flask import Flask, jsonify, send_file, request
import os
from datetime import datetime
import logging
from manufacturing_analytics import ManufacturingAnalytics
import threading
import zipfile
import json
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app for API
app = Flask(__name__)

# Configuration
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.environ.get('DATABASE_NAME', 'manufacturing_db')
OUTPUT_DIR = os.environ.get('OUTPUT_DIR', './analytics_output')
GRAFANA_CSV_DIR = os.environ.get('GRAFANA_CSV_DIR', '/var/lib/grafana/csv')
SCHEDULE_INTERVAL = int(os.environ.get('SCHEDULE_INTERVAL_MINUTES', 60))

# Global analytics instance
analytics = None
last_run_status = {
    'status': 'pending',
    'timestamp': None,
    'files_generated': 0,
    'error': None
}

def handle_errors(f):
    """Decorator to handle API errors gracefully"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    return decorated_function

def initialize_analytics():
    """Initialize analytics service with error handling"""
    global analytics
    try:
        analytics = ManufacturingAnalytics(MONGO_URI, DATABASE_NAME)
        logger.info("Analytics service initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize analytics service: {str(e)}")
        return False

def copy_files_to_grafana():
    """Copy CSV files to Grafana data directory"""
    try:
        if os.path.exists(GRAFANA_CSV_DIR):
            # Copy all CSV files to Grafana directory
            for filename in os.listdir(OUTPUT_DIR):
                if filename.endswith('.csv'):
                    src = os.path.join(OUTPUT_DIR, filename)
                    dst = os.path.join(GRAFANA_CSV_DIR, filename)
                    shutil.copy2(src, dst)
                    logger.info(f"Copied {filename} to Grafana directory")
        else:
            logger.warning(f"Grafana CSV directory not found: {GRAFANA_CSV_DIR}")
    except Exception as e:
        logger.error(f"Error copying files to Grafana: {str(e)}")

def run_analytics():
    """Run the analytics process and generate CSV files"""
    global last_run_status
    
    if not analytics:
        if not initialize_analytics():
            last_run_status.update({
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': 'Failed to initialize analytics service'
            })
            return False
    
    try:
        logger.info("Starting analytics generation...")
        last_run_status.update({
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'error': None
        })
        
        # Create output directory if it doesn't exist
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Generate analytics
        summary = analytics.export_to_csv(OUTPUT_DIR)
        
        # Copy files to Grafana directory
        copy_files_to_grafana()
        
        # Count generated files
        files_generated = len([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.csv')])
        
        last_run_status.update({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'files_generated': files_generated,
            'error': None,
            'summary': summary
        })
        
        logger.info(f"Analytics completed successfully: {summary}")
        return True
        
    except Exception as e:
        error_msg = f"Error during analytics generation: {str(e)}"
        logger.error(error_msg)
        last_run_status.update({
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'error': error_msg
        })
        return False

@app.route('/health')
@handle_errors
def health():
    """Health check endpoint with detailed status"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'manufacturing-analytics',
        'version': '1.0.0',
        'analytics_service': 'connected' if analytics else 'disconnected',
        'last_run': last_run_status,
        'output_directory': OUTPUT_DIR,
        'files_count': len([f for f in os.listdir(OUTPUT_DIR) if os.path.isfile(os.path.join(OUTPUT_DIR, f))]) if os.path.exists(OUTPUT_DIR) else 0
    }
    
    # Check if we can connect to MongoDB
    try:
        if analytics:
            # Test connection by counting documents
            analytics.orders_collection.count_documents({}, limit=1)
            health_status['mongodb'] = 'connected'
        else:
            health_status['mongodb'] = 'disconnected'
    except Exception as e:
        health_status['mongodb'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

@app.route('/analytics/run', methods=['POST'])
@handle_errors
def trigger_analytics():
    """Manually trigger analytics generation"""
    force = request.args.get('force', 'false').lower() == 'true'
    
    # Check if already running
    if last_run_status['status'] == 'running' and not force:
        return jsonify({
            'status': 'error',
            'message': 'Analytics generation already in progress',
            'timestamp': datetime.now().isoformat()
        }), 409
    
    success = run_analytics()
    if success:
        return jsonify({
            'status': 'success',
            'message': 'Analytics generated successfully',
            'timestamp': datetime.now().isoformat(),
            'last_run': last_run_status
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate analytics',
            'timestamp': datetime.now().isoformat(),
            'last_run': last_run_status
        }), 500

@app.route('/analytics/status')
@handle_errors
def get_status():
    """Get current analytics status"""
    return jsonify({
        'current_status': last_run_status,
        'next_scheduled_run': schedule.next_run().isoformat() if schedule.jobs else None,
        'schedule_interval_minutes': SCHEDULE_INTERVAL
    })

@app.route('/analytics/files')
@handle_errors
def list_files():
    """List available analytics files with metadata"""
    files = []
    if os.path.exists(OUTPUT_DIR):
        for filename in os.listdir(OUTPUT_DIR):
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.isfile(filepath):
                file_info = {
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'size_mb': round(os.path.getsize(filepath) / (1024*1024), 2),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat(),
                    'type': 'csv' if filename.endswith('.csv') else 'json' if filename.endswith('.json') else 'other'
                }
                files.append(file_info)
    
    return jsonify({
        'files': sorted(files, key=lambda x: x['modified'], reverse=True),
        'total_files': len(files),
        'total_size_mb': round(sum(f['size'] for f in files) / (1024*1024), 2)
    })

@app.route('/analytics/download/<filename>')
@handle_errors
def download_file(filename):
    """Download a specific analytics file"""
    # Security: prevent path traversal
    filename = os.path.basename(filename)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if os.path.exists(filepath) and os.path.isfile(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/analytics/download-all')
@handle_errors
def download_all():
    """Download all analytics files as a zip"""
    zip_path = os.path.join(OUTPUT_DIR, f'analytics_all_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename in os.listdir(OUTPUT_DIR):
            if filename != os.path.basename(zip_path):  # Don't include the zip file itself
                filepath = os.path.join(OUTPUT_DIR, filename)
                if os.path.isfile(filepath):
                    zipf.write(filepath, filename)
    
    return send_file(zip_path, as_attachment=True)

@app.route('/analytics/summary')
@handle_errors
def get_summary():
    """Get the latest summary statistics"""
    summary_path = os.path.join(OUTPUT_DIR, 'summary_statistics.json')
    if os.path.exists(summary_path):
        try:
            with open(summary_path, 'r') as f:
                summary = json.load(f)
            
            # Add metadata
            summary['file_generated'] = datetime.fromtimestamp(os.path.getmtime(summary_path)).isoformat()
            summary['last_analytics_run'] = last_run_status['timestamp']
            
            return jsonify(summary)
        except json.JSONDecodeError as e:
            return jsonify({'error': f'Invalid JSON in summary file: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Summary not found. Run analytics first.'}), 404

@app.route('/analytics/config')
@handle_errors
def get_config():
    """Get current service configuration"""
    return jsonify({
        'mongo_uri': MONGO_URI.replace(MONGO_URI.split('@')[0].split('//')[1], '***') if '@' in MONGO_URI else MONGO_URI,
        'database_name': DATABASE_NAME,
        'output_directory': OUTPUT_DIR,
        'grafana_csv_directory': GRAFANA_CSV_DIR,
        'schedule_interval_minutes': SCHEDULE_INTERVAL,
        'service_info': {
            'name': 'manufacturing-analytics',
            'version': '1.0.0',
            'uptime': time.time() - start_time if 'start_time' in globals() else 0
        }
    })

def run_scheduler():
    """Run the scheduled analytics generation"""
    logger.info(f"Starting scheduler with {SCHEDULE_INTERVAL} minute intervals")
    
    # Run once on startup
    logger.info("Running initial analytics generation...")
    run_analytics()
    
    # Schedule regular runs
    schedule.every(SCHEDULE_INTERVAL).minutes.do(run_analytics)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    # Record start time for uptime calculation
    start_time = time.time()
    
    # Initialize analytics service
    if not initialize_analytics():
        logger.error("Failed to initialize analytics service. Some endpoints may not work.")
    
    # Start scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start Flask API
    logger.info("Starting Flask API server...")
    app.run(host='0.0.0.0', port=5000, debug=False)