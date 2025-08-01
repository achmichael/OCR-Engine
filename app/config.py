"""
Application Configuration
========================

Konfigurasi aplikasi OCR ML Engine dengan berbagai environment settings.

Author: AI Assistant
Date: August 2025
"""

import os
from pathlib import Path


class Config:
    """
    Base configuration class dengan settings default
    """
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ocr-ml-engine-secret-key-2025'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    RESULTS_FOLDER = os.environ.get('RESULTS_FOLDER') or 'results'
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    ALLOWED_PDF_EXTENSIONS = {'pdf'}
    
    # OCR Engine settings
    OCR_DEFAULT_LANGUAGES = ['en', 'id']
    OCR_DEFAULT_ENGINE = 'both'  # tesseract, easyocr, both
    OCR_DEFAULT_ENHANCEMENT_LEVEL = 2  # 1=basic, 2=medium, 3=aggressive
    OCR_USE_GPU = os.environ.get('OCR_USE_GPU', 'False').lower() == 'true'
    OCR_MIN_CONFIDENCE = 30
    
    # Tesseract configuration
    TESSERACT_OEM = 3  # OCR Engine Mode
    TESSERACT_PSM = 6  # Page Segmentation Mode
    TESSERACT_CONFIG = '--oem 3 --psm 6'
    
    # EasyOCR configuration
    EASYOCR_DETAIL_LEVEL = 1
    EASYOCR_PARAGRAPH = True
    EASYOCR_WIDTH_THS = 0.7
    EASYOCR_HEIGHT_THS = 0.7
    
    # PDF processing settings
    PDF_DPI = 300
    PDF_IMAGE_FORMAT = 'JPEG'
    PDF_THREAD_COUNT = 2
    PDF_TRY_DIRECT_EXTRACTION = True
    PDF_MIN_DIRECT_TEXT_LENGTH = 50
    
    # Performance settings
    BATCH_SIZE = 10
    ENABLE_MULTIPROCESSING = False
    PROCESS_COUNT = 0  # 0 = auto detect
    MEMORY_LIMIT_MB = 1000
    AUTO_CLEANUP = True
    
    # Cache settings
    ENABLE_CACHE = False
    CACHE_DIR = 'cache'
    CACHE_EXPIRY_HOURS = 24
    MAX_CACHE_SIZE_MB = 500
    
    # Logging settings
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    ENABLE_FILE_LOGGING = True
    LOG_FILE = 'logs/ocr_app.log'
    MAX_LOG_SIZE_MB = 10
    BACKUP_COUNT = 5
    
    # API settings
    API_TITLE = 'OCR ML Engine API'
    API_VERSION = '1.0.0'
    API_DESCRIPTION = 'Advanced OCR API untuk text extraction dari images dan PDFs'
    
    @staticmethod
    def init_app(app):
        """
        Initialize application dengan configuration ini
        
        Args:
            app: Flask application instance
        """
        pass


class DevelopmentConfig(Config):
    """
    Development environment configuration
    """
    DEBUG = True
    TESTING = False
    
    # Development-specific settings
    OCR_USE_GPU = False  # Disable GPU untuk development
    LOG_LEVEL = 'DEBUG'
    ENABLE_FILE_LOGGING = True
    
    # Relaxed file size untuk development
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        app.logger.info('Development configuration loaded')


class ProductionConfig(Config):
    """
    Production environment configuration
    """
    DEBUG = False
    TESTING = False
    
    # Production-specific settings
    OCR_USE_GPU = os.environ.get('OCR_USE_GPU', 'False').lower() == 'true'
    LOG_LEVEL = 'INFO'
    ENABLE_FILE_LOGGING = True
    
    # Stricter settings untuk production
    MAX_CONTENT_LENGTH = 25 * 1024 * 1024  # 25MB untuk production
    ENABLE_MULTIPROCESSING = True
    ENABLE_CACHE = True
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        
        # Setup production logging
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/ocr_app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Production configuration loaded')


class TestingConfig(Config):
    """
    Testing environment configuration
    """
    DEBUG = True
    TESTING = True
    
    # Testing-specific settings
    WTF_CSRF_ENABLED = False
    OCR_USE_GPU = False
    UPLOAD_FOLDER = 'tests/uploads'
    RESULTS_FOLDER = 'tests/results'
    
    # Smaller limits untuk testing
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    BATCH_SIZE = 2
    
    # Disable caching untuk testing
    ENABLE_CACHE = False
    ENABLE_FILE_LOGGING = False
    
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        app.logger.info('Testing configuration loaded')


# Configuration dictionary untuk easy access
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(config_name=None):
    """
    Get configuration class berdasarkan environment
    
    Args:
        config_name (str): Nama configuration ('development', 'production', 'testing')
        
    Returns:
        Config: Configuration class
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config.get(config_name, DevelopmentConfig)
