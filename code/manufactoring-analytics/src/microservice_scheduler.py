import schedule
import time
from flask import Flask, jsonify, send_file
import os
from datetime import datetime
import logging
from manufacturing_analytics import ManufacturingAnalytics
import threading
import zipfile

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
SCHEDULE_INTERVAL = int(os.environ.get('SCHEDULE_INTERVAL_MINUTES', 60))

# Global analytics instance
analytics = ManufacturingAnalytics(MONGO_URI, DATABASE_NAME)

def run_analytics():
    """Run the analytics process and generate CSV files"""
    try:
        logger.info("Starting analytics generation...")
        summary = analytics.export_to_csv(OUTPUT_DIR)
        logger.info(f"Analytics completed successfully: {summary}")
        return True
    except Exception as e:
        logger.error(f"Error during analytics generation: {str(e)}")
        return False

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/analytics/run', methods=['POST'])
def trigger_analytics():
    """Manually trigger analytics generation"""
    success = run_analytics()
    if success:
        return jsonify({
            'status': 'success',
            'message': 'Analytics generated successfully',
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to generate analytics',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/analytics/files')
def list_files():
    """List available analytics files"""
    files = []
    if os.path.exists(OUTPUT_DIR):
        for filename in os.listdir(OUTPUT_DIR):
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                })
    return jsonify({'files': files})

@app.route('/analytics/download/<filename>')
def download_file(filename):
    """Download a specific analytics file"""
    filepath = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/analytics/download-all')
def download_all():
    """Download all analytics files as a zip"""
    zip_path = os.path.join(OUTPUT_DIR, 'analytics_all.zip')
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in os.listdir(OUTPUT_DIR):
            if filename != 'analytics_all.zip':
                filepath = os.path.join(OUTPUT_DIR, filename)
                if os.path.isfile(filepath):
                    zipf.write(filepath, filename)
    
    return send_file(zip_path, as_attachment=True)

@app.route('/analytics/summary')
def get_summary():
    """Get the latest summary statistics"""
    summary_path = os.path.join(OUTPUT_DIR, 'summary_statistics.json')
    if os.path.exists(summary_path):
        with open(summary_path, 'r') as f:
            import json
            summary = json.load(f)
        return jsonify(summary)
    else:
        return jsonify({'error': 'Summary not found. Run analytics first.'}), 404

def run_scheduler():
    """Run the scheduled analytics generation"""
    # Run once on startup
    run_analytics()
    
    # Schedule regular runs
    schedule.every(SCHEDULE_INTERVAL).minutes.do(run_analytics)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    # Start scheduler in a separate thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Start Flask API
    app.run(host='0.0.0.0', port=5000, debug=False)