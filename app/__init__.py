"""
Flask App Initialization
========================

Inisialisasi Flask application dengan konfigurasi dan registrasi blueprints.

Author: AI Assistant
Date: August 2025
"""

from flask import Flask
from flask_cors import CORS
import logging
import os
from pathlib import Path

def create_app(config_name='default'):
    """
    Factory function untuk membuat Flask application
    
    Args:
        config_name (str): Nama konfigurasi yang akan digunakan
        
    Returns:
        Flask: Configured Flask application instance
    """
    # Inisialisasi Flask app
    app = Flask(__name__)
    
    # Load konfigurasi
    from app.config import Config
    app.config.from_object(Config)
    
    # Setup CORS untuk cross-origin requests
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Setup logging
    setup_logging(app)
    
    # Buat directories yang diperlukan
    create_required_directories(app)
    
    # Register blueprints (routes)
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    app.logger.info("Flask OCR application initialized successfully")
    
    return app


def setup_logging(app):
    """
    Setup logging configuration untuk aplikasi
    
    Args:
        app (Flask): Flask application instance
    """
    if not app.debug and not app.testing:
        # Setup file handler untuk production
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = logging.FileHandler('logs/ocr_app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('OCR ML Engine startup')


def create_required_directories(app):
    """
    Buat directories yang diperlukan untuk aplikasi
    
    Args:
        app (Flask): Flask application instance
    """
    required_dirs = [
        app.config.get('UPLOAD_FOLDER', 'uploads'),
        app.config.get('RESULTS_FOLDER', 'results'),
        'logs',
        'cache'
    ]
    
    for directory in required_dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
        app.logger.debug(f"Directory ensured: {directory}")


def register_blueprints(app):
    """
    Register semua blueprints untuk routing
    
    Args:
        app (Flask): Flask application instance
    """
    from app.routes import api_bp
    
    # Register API blueprint dengan prefix
    app.register_blueprint(api_bp, url_prefix='/api')
    
    app.logger.info("Blueprints registered successfully")


def register_error_handlers(app):
    """
    Register custom error handlers
    
    Args:
        app (Flask): Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors"""
        return {
            'error': 'Resource not found',
            'status_code': 404,
            'message': 'The requested resource was not found on this server'
        }, 404
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handle file size too large errors"""
        return {
            'error': 'File too large',
            'status_code': 413,
            'message': f'File size exceeds maximum limit of {app.config.get("MAX_CONTENT_LENGTH", 50)}MB'
        }, 413
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle internal server errors"""
        app.logger.error(f'Server Error: {error}')
        return {
            'error': 'Internal server error',
            'status_code': 500,
            'message': 'An internal server error occurred'
        }, 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Handle unexpected exceptions"""
        app.logger.error(f'Unhandled Exception: {e}')
        return {
            'error': 'Unexpected error',
            'status_code': 500,
            'message': 'An unexpected error occurred'
        }, 500
    
    app.logger.info("Error handlers registered successfully")
