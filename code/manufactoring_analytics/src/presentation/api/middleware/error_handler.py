# src/presentation/api/middleware/error_handler.py
from flask import jsonify
from werkzeug.exceptions import HTTPException
from ....domain.exceptions import (
    DomainException, 
    OrderNotFoundException,
    MachineNotFoundException,
    InvalidDateRangeException,
    ExportFailedException,
    SchedulerException
)
import logging

logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers for the Flask app"""
    
    @app.errorhandler(DomainException)
    def handle_domain_exception(e):
        """Handle domain exceptions"""
        logger.error(f"Domain exception: {str(e)}")
        
        if isinstance(e, OrderNotFoundException):
            status_code = 404
        elif isinstance(e, MachineNotFoundException):
            status_code = 404
        elif isinstance(e, InvalidDateRangeException):
            status_code = 400
        elif isinstance(e, ExportFailedException):
            status_code = 500
        elif isinstance(e, SchedulerException):
            status_code = 503
        else:
            status_code = 500
        
        return jsonify({
            'error': {
                'type': e.__class__.__name__,
                'message': str(e)
            }
        }), status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Handle HTTP exceptions"""
        return jsonify({
            'error': {
                'type': 'HTTPException',
                'message': e.description,
                'code': e.code
            }
        }), e.code
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        """Handle unexpected errors"""
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        
        # Don't expose internal errors in production
        if app.config.get('DEBUG'):
            message = str(e)
        else:
            message = 'An unexpected error occurred'
        
        return jsonify({
            'error': {
                'type': 'InternalServerError',
                'message': message
            }
        }), 500