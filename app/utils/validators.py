"""
Request dan File Validators
===========================

Utilities untuk validasi request dan file uploads.

Author: AI Assistant
Date: August 2025
"""

import os
import magic
from typing import Dict, Any, List, Optional
from werkzeug.datastructures import FileStorage
from flask import Request


def validate_request(request: Request, file_required: bool = False, files_required: bool = False) -> Dict[str, Any]:
    """
    Validate incoming HTTP request
    
    Args:
        request (Request): Flask request object
        file_required (bool): Apakah single file diperlukan
        files_required (bool): Apakah multiple files diperlukan
    
    Returns:
        dict: Validation result dengan 'valid' dan 'message'
    """
    try:
        # Check content type
        if not request.content_type:
            return {
                'valid': False,
                'message': 'Content-Type header is required'
            }
        
        # Check for multipart data jika file diperlukan
        if (file_required or files_required) and not request.content_type.startswith('multipart/form-data'):
            return {
                'valid': False,
                'message': 'multipart/form-data content type required for file uploads'
            }
        
        # Check single file requirement
        if file_required:
            if 'file' not in request.files:
                return {
                    'valid': False,
                    'message': 'No file field found in request'
                }
            
            file = request.files['file']
            if file.filename == '':
                return {
                    'valid': False,
                    'message': 'No file selected'
                }
        
        # Check multiple files requirement
        if files_required:
            files = request.files.getlist('files')
            if not files:
                return {
                    'valid': False,
                    'message': 'No files field found in request'
                }
            
            if all(f.filename == '' for f in files):
                return {
                    'valid': False,
                    'message': 'No files selected'
                }
        
        return {
            'valid': True,
            'message': 'Request is valid'
        }
        
    except Exception as e:
        return {
            'valid': False,
            'message': f'Request validation error: {str(e)}'
        }


def validate_file(file: FileStorage, file_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate uploaded file
    
    Args:
        file (FileStorage): Uploaded file object
        file_type (str): Expected file type ('image' atau 'pdf')
        config (dict): Application configuration
    
    Returns:
        dict: Validation result dengan 'valid' dan 'message'
    """
    try:
        if not file or file.filename == '':
            return {
                'valid': False,
                'message': 'No file provided'
            }
        
        filename = file.filename.lower()
        
        # Check file extension
        if file_type == 'image':
            allowed_extensions = config.get('ALLOWED_IMAGE_EXTENSIONS', {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'})
            if not any(filename.endswith(ext) for ext in allowed_extensions):
                return {
                    'valid': False,
                    'message': f'Invalid image format. Allowed: {", ".join(allowed_extensions)}'
                }
        
        elif file_type == 'pdf':
            allowed_extensions = config.get('ALLOWED_PDF_EXTENSIONS', {'.pdf'})
            if not any(filename.endswith(ext) for ext in allowed_extensions):
                return {
                    'valid': False,
                    'message': f'Invalid PDF format. Allowed: {", ".join(allowed_extensions)}'
                }
        
        # Check file size
        max_size = config.get('MAX_FILE_SIZE', 50 * 1024 * 1024)  # 50MB default
        
        # Get current position dan seek to end untuk measure size
        current_pos = file.tell()
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(current_pos)  # Reset position
        
        if file_size > max_size:
            max_size_mb = max_size // (1024 * 1024)
            return {
                'valid': False,
                'message': f'File too large. Maximum size: {max_size_mb}MB'
            }
        
        if file_size == 0:
            return {
                'valid': False,
                'message': 'File is empty'
            }
        
        # Validate MIME type jika python-magic tersedia
        try:
            # Read a small chunk untuk MIME detection
            file.seek(0)
            chunk = file.read(1024)
            file.seek(0)  # Reset position
            
            if chunk:
                mime_type = magic.from_buffer(chunk, mime=True)
                
                if file_type == 'image':
                    valid_mimes = {
                        'image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 
                        'image/tiff', 'image/gif', 'image/webp'
                    }
                    if mime_type not in valid_mimes:
                        return {
                            'valid': False,
                            'message': f'Invalid image MIME type: {mime_type}'
                        }
                
                elif file_type == 'pdf':
                    if mime_type != 'application/pdf':
                        return {
                            'valid': False,
                            'message': f'Invalid PDF MIME type: {mime_type}'
                        }
            
        except ImportError:
            # python-magic not available, skip MIME validation
            pass
        except Exception:
            # MIME detection failed, continue without it
            pass
        
        return {
            'valid': True,
            'message': 'File is valid',
            'file_size': file_size,
            'filename': file.filename
        }
        
    except Exception as e:
        return {
            'valid': False,
            'message': f'File validation error: {str(e)}'
        }


def validate_ocr_parameters(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate OCR processing parameters
    
    Args:
        params (dict): OCR parameters to validate
    
    Returns:
        dict: Validation result dengan validated parameters
    """
    try:
        validated = {}
        errors = []
        
        # Enhancement level validation
        enhancement_level = params.get('enhancement_level', 2)
        try:
            enhancement_level = int(enhancement_level)
            if enhancement_level not in [1, 2, 3]:
                errors.append('enhancement_level must be 1, 2, or 3')
            else:
                validated['enhancement_level'] = enhancement_level
        except (ValueError, TypeError):
            errors.append('enhancement_level must be an integer')
        
        # Engine validation
        engine = params.get('engine', 'both')
        valid_engines = ['tesseract', 'easyocr', 'both']
        if engine not in valid_engines:
            errors.append(f'engine must be one of: {", ".join(valid_engines)}')
        else:
            validated['engine'] = engine
        
        # Languages validation
        languages = params.get('languages', 'en,id')
        if isinstance(languages, str):
            language_list = [lang.strip() for lang in languages.split(',')]
            # Basic language code validation (2-3 character codes)
            valid_languages = []
            for lang in language_list:
                if len(lang) in [2, 3] and lang.isalpha():
                    valid_languages.append(lang.lower())
                else:
                    errors.append(f'Invalid language code: {lang}')
            
            if valid_languages:
                validated['languages'] = valid_languages
        else:
            errors.append('languages must be a comma-separated string')
        
        # Page range validation (untuk PDF)
        if 'page_start' in params:
            try:
                page_start = int(params['page_start'])
                if page_start < 1:
                    errors.append('page_start must be >= 1')
                else:
                    validated['page_start'] = page_start
            except (ValueError, TypeError):
                errors.append('page_start must be an integer')
        
        if 'page_end' in params:
            try:
                page_end = int(params['page_end'])
                if page_end < 1:
                    errors.append('page_end must be >= 1')
                else:
                    validated['page_end'] = page_end
            except (ValueError, TypeError):
                errors.append('page_end must be an integer')
        
        # Check page range consistency
        if 'page_start' in validated and 'page_end' in validated:
            if validated['page_start'] > validated['page_end']:
                errors.append('page_start must be <= page_end')
        
        # Try direct extraction (untuk PDF)
        if 'try_direct' in params:
            try:
                validated['try_direct'] = str(params['try_direct']).lower() in ['true', '1', 'yes', 'on']
            except Exception:
                errors.append('try_direct must be a boolean value')
        
        if errors:
            return {
                'valid': False,
                'message': 'Parameter validation failed',
                'errors': errors
            }
        
        return {
            'valid': True,
            'message': 'Parameters are valid',
            'validated_params': validated
        }
        
    except Exception as e:
        return {
            'valid': False,
            'message': f'Parameter validation error: {str(e)}'
        }


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename untuk safe storage
    
    Args:
        filename (str): Original filename
    
    Returns:
        str: Sanitized filename
    """
    if not filename:
        return 'unnamed_file'
    
    # Remove path separators
    filename = os.path.basename(filename)
    
    # Replace dangerous characters
    dangerous_chars = '<>:"/\\|?*'
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Remove consecutive underscores
    while '__' in filename:
        filename = filename.replace('__', '_')
    
    # Remove leading/trailing underscores dan dots
    filename = filename.strip('_.')
    
    # Ensure filename is not empty
    if not filename:
        return 'unnamed_file'
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        max_name_length = 255 - len(ext)
        filename = name[:max_name_length] + ext
    
    return filename


def validate_result_id(result_id: str) -> Dict[str, Any]:
    """
    Validate result ID format
    
    Args:
        result_id (str): Result ID to validate
    
    Returns:
        dict: Validation result
    """
    try:
        if not result_id:
            return {
                'valid': False,
                'message': 'Result ID is required'
            }
        
        # Check format (should be UUID-like)
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        
        if not re.match(uuid_pattern, result_id.lower()):
            return {
                'valid': False,
                'message': 'Invalid result ID format'
            }
        
        return {
            'valid': True,
            'message': 'Result ID is valid'
        }
        
    except Exception as e:
        return {
            'valid': False,
            'message': f'Result ID validation error: {str(e)}'
        }
