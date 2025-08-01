"""
API Routes
==========

Blueprint untuk mendefinisikan semua API endpoints dan routing.

Author: AI Assistant
Date: August 2025
"""

from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
import uuid
import time

# Import controllers
from app.controllers.ocr_controller import OCRController
from app.controllers.health_controller import HealthController
from app.utils.validators import validate_file, validate_request

# Create blueprint untuk API routes
api_bp = Blueprint('api', __name__)

# Initialize controllers
ocr_controller = OCRController()
health_controller = HealthController()


@api_bp.route('/', methods=['GET'])
def api_info():
    """
    API information endpoint
    
    Returns:
        dict: API information dan available endpoints
    """
    return jsonify({
        'service': current_app.config.get('API_TITLE', 'OCR ML Engine API'),
        'version': current_app.config.get('API_VERSION', '1.0.0'),
        'description': current_app.config.get('API_DESCRIPTION', 'OCR API untuk text extraction'),
        'status': 'running',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'endpoints': {
            'GET /api/': 'API information',
            'GET /api/health': 'Health check',
            'POST /api/ocr/image': 'OCR untuk single image',
            'POST /api/ocr/batch': 'OCR untuk multiple images',
            'POST /api/ocr/pdf': 'OCR untuk PDF file',
            'GET /api/results/<result_id>': 'Get OCR result by ID'
        },
        'supported_formats': {
            'images': list(current_app.config.get('ALLOWED_IMAGE_EXTENSIONS', [])),
            'documents': list(current_app.config.get('ALLOWED_PDF_EXTENSIONS', []))
        }
    })


@api_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint untuk monitoring
    
    Returns:
        dict: System health status
    """
    return health_controller.get_health_status()


@api_bp.route('/ocr/image', methods=['POST'])
def ocr_single_image():
    """
    OCR endpoint untuk single image file
    
    Expected:
        - multipart/form-data dengan 'file' field
        - Optional: enhancement_level (1-3)
        - Optional: engine ('tesseract', 'easyocr', 'both')
        - Optional: languages (comma-separated)
    
    Returns:
        dict: OCR result dengan extracted text
    """
    try:
        # Validate request
        validation_result = validate_request(request, file_required=True)
        if not validation_result['valid']:
            return jsonify({
                'error': validation_result['message'],
                'status_code': 400
            }), 400
        
        file = request.files['file']
        
        # Validate file
        file_validation = validate_file(file, 'image', current_app.config)
        if not file_validation['valid']:
            return jsonify({
                'error': file_validation['message'],
                'status_code': 400
            }), 400
        
        # Get optional parameters
        params = {
            'enhancement_level': int(request.form.get('enhancement_level', 
                                   current_app.config.get('OCR_DEFAULT_ENHANCEMENT_LEVEL', 2))),
            'engine': request.form.get('engine', 
                                     current_app.config.get('OCR_DEFAULT_ENGINE', 'both')),
            'languages': request.form.get('languages', 
                                        ','.join(current_app.config.get('OCR_DEFAULT_LANGUAGES', ['en', 'id'])))
        }
        
        # Process dengan controller
        result = ocr_controller.process_single_image(file, params)
        
        return jsonify(result), 200 if result.get('success', False) else 500
        
    except Exception as e:
        current_app.logger.error(f"OCR image processing error: {e}")
        return jsonify({
            'error': 'Processing failed',
            'message': str(e),
            'status_code': 500
        }), 500


@api_bp.route('/ocr/batch', methods=['POST'])
def ocr_batch_images():
    """
    OCR endpoint untuk multiple image files
    
    Expected:
        - multipart/form-data dengan multiple 'files' fields
        - Optional: enhancement_level (1-3)
        - Optional: engine ('tesseract', 'easyocr', 'both')
        - Optional: languages (comma-separated)
    
    Returns:
        dict: Batch OCR results
    """
    try:
        # Validate request untuk batch
        validation_result = validate_request(request, files_required=True)
        if not validation_result['valid']:
            return jsonify({
                'error': validation_result['message'],
                'status_code': 400
            }), 400
        
        files = request.files.getlist('files')
        
        # Validate semua files
        validated_files = []
        for file in files:
            file_validation = validate_file(file, 'image', current_app.config)
            if file_validation['valid']:
                validated_files.append(file)
        
        if not validated_files:
            return jsonify({
                'error': 'No valid image files found',
                'status_code': 400
            }), 400
        
        # Get parameters
        params = {
            'enhancement_level': int(request.form.get('enhancement_level', 
                                   current_app.config.get('OCR_DEFAULT_ENHANCEMENT_LEVEL', 2))),
            'engine': request.form.get('engine', 
                                     current_app.config.get('OCR_DEFAULT_ENGINE', 'both')),
            'languages': request.form.get('languages', 
                                        ','.join(current_app.config.get('OCR_DEFAULT_LANGUAGES', ['en', 'id'])))
        }
        
        # Process dengan controller
        result = ocr_controller.process_batch_images(validated_files, params)
        
        return jsonify(result), 200 if result.get('success', False) else 500
        
    except Exception as e:
        current_app.logger.error(f"Batch OCR processing error: {e}")
        return jsonify({
            'error': 'Batch processing failed',
            'message': str(e),
            'status_code': 500
        }), 500


@api_bp.route('/ocr/pdf', methods=['POST'])
def ocr_pdf_file():
    """
    OCR endpoint untuk PDF files
    
    Expected:
        - multipart/form-data dengan 'file' field
        - Optional: page_start, page_end untuk range processing
        - Optional: enhancement_level (1-3)
        - Optional: try_direct (boolean)
    
    Returns:
        dict: PDF OCR results
    """
    try:
        # Validate request
        validation_result = validate_request(request, file_required=True)
        if not validation_result['valid']:
            return jsonify({
                'error': validation_result['message'],
                'status_code': 400
            }), 400
        
        file = request.files['file']
        
        # Validate PDF file
        file_validation = validate_file(file, 'pdf', current_app.config)
        if not file_validation['valid']:
            return jsonify({
                'error': file_validation['message'],
                'status_code': 400
            }), 400
        
        # Get parameters
        params = {
            'enhancement_level': int(request.form.get('enhancement_level', 
                                   current_app.config.get('OCR_DEFAULT_ENHANCEMENT_LEVEL', 2))),
            'page_start': request.form.get('page_start', type=int),
            'page_end': request.form.get('page_end', type=int),
            'try_direct': request.form.get('try_direct', 'true').lower() == 'true'
        }
        
        # Process dengan controller
        result = ocr_controller.process_pdf_file(file, params)
        
        return jsonify(result), 200 if result.get('success', False) else 500
        
    except Exception as e:
        current_app.logger.error(f"PDF OCR processing error: {e}")
        return jsonify({
            'error': 'PDF processing failed',
            'message': str(e),
            'status_code': 500
        }), 500


@api_bp.route('/results/<result_id>', methods=['GET'])
def get_result(result_id):
    """
    Get detailed OCR result berdasarkan result ID
    
    Args:
        result_id (str): ID hasil OCR yang disimpan
    
    Returns:
        dict: Detailed OCR result data
    """
    try:
        result = ocr_controller.get_result_by_id(result_id)
        
        if result:
            return jsonify(result), 200
        else:
            return jsonify({
                'error': 'Result not found',
                'message': f'No result found with ID: {result_id}',
                'status_code': 404
            }), 404
            
    except Exception as e:
        current_app.logger.error(f"Failed to retrieve result {result_id}: {e}")
        return jsonify({
            'error': 'Failed to retrieve result',
            'message': str(e),
            'status_code': 500
        }), 500


@api_bp.route('/models/info', methods=['GET'])
def models_info():
    """
    Get information tentang OCR models yang tersedia
    
    Returns:
        dict: Information tentang available models
    """
    try:
        info = ocr_controller.get_models_info()
        return jsonify(info), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to get models info: {e}")
        return jsonify({
            'error': 'Failed to get models information',
            'message': str(e),
            'status_code': 500
        }), 500


# Error handlers untuk blueprint
@api_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request errors"""
    return jsonify({
        'error': 'Bad request',
        'message': 'The request could not be understood or was missing required parameters',
        'status_code': 400
    }), 400


@api_bp.errorhandler(413)
def payload_too_large(error):
    """Handle payload too large errors"""
    max_size = current_app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024)
    max_size_mb = max_size // (1024 * 1024)
    
    return jsonify({
        'error': 'File too large',
        'message': f'File size exceeds maximum limit of {max_size_mb}MB',
        'status_code': 413
    }), 413


@api_bp.errorhandler(415)
def unsupported_media_type(error):
    """Handle unsupported media type errors"""
    return jsonify({
        'error': 'Unsupported media type',
        'message': 'The uploaded file type is not supported',
        'status_code': 415
    }), 415
