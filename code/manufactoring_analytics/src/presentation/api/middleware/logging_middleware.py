# src/presentation/api/middleware/logging_middleware.py
from flask import request, g
import time
import logging
import uuid

logger = logging.getLogger(__name__)

def register_logging_middleware(app):
    """Register logging middleware for the Flask app"""
    
    @app.before_request
    def before_request():
        """Log request start"""
        g.request_id = str(uuid.uuid4())[:8]
        g.start_time = time.time()
        
        logger.info(
            f"[{g.request_id}] {request.method} {request.path} "
            f"from {request.remote_addr}"
        )
    
    @app.after_request
    def after_request(response):
        """Log request completion"""
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            
            logger.info(
                f"[{g.request_id}] {request.method} {request.path} "
                f"completed with {response.status_code} in {duration:.3f}s"
            )
            
            # Add request ID to response headers
            response.headers['X-Request-ID'] = g.request_id
            response.headers['X-Process-Time'] = str(duration)
        
        return response