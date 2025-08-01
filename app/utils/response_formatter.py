"""
Response Formatter
==================

Utility untuk formatting consistent API responses.

Author: AI Assistant
Date: August 2025
"""

import time
from typing import Dict, Any, Optional, Union


class ResponseFormatter:
    """
    Class untuk formatting consistent API responses
    
    Provides standard format untuk:
    - Success responses
    - Error responses  
    - Validation responses
    - Data responses
    """
    
    def __init__(self):
        """Initialize ResponseFormatter"""
        pass
    
    
    def success_response(self, message: str, data: Optional[Any] = None, 
                        status_code: int = 200, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format success response
        
        Args:
            message (str): Success message
            data (any): Response data
            status_code (int): HTTP status code
            meta (dict): Additional metadata
        
        Returns:
            dict: Formatted success response
        """
        response = {
            'success': True,
            'message': message,
            'status_code': status_code,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if data is not None:
            response['data'] = data
        
        if meta:
            response['meta'] = meta
        
        return response
    
    
    def error_response(self, message: str, error_details: Optional[str] = None, 
                      status_code: int = 500, error_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Format error response
        
        Args:
            message (str): Error message
            error_details (str): Detailed error information
            status_code (int): HTTP status code
            error_code (str): Application-specific error code
        
        Returns:
            dict: Formatted error response
        """
        response = {
            'success': False,
            'error': message,
            'status_code': status_code,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if error_details:
            response['details'] = error_details
        
        if error_code:
            response['error_code'] = error_code
        
        return response
    
    
    def validation_error_response(self, message: str, validation_errors: Dict[str, Any], 
                                 status_code: int = 400) -> Dict[str, Any]:
        """
        Format validation error response
        
        Args:
            message (str): Main validation error message
            validation_errors (dict): Detailed validation errors
            status_code (int): HTTP status code
        
        Returns:
            dict: Formatted validation error response
        """
        return {
            'success': False,
            'error': message,
            'validation_errors': validation_errors,
            'status_code': status_code,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    
    def paginated_response(self, data: list, total: int, page: int, per_page: int, 
                          message: str = "Data retrieved successfully") -> Dict[str, Any]:
        """
        Format paginated response
        
        Args:
            data (list): Paginated data
            total (int): Total number of items
            page (int): Current page number
            per_page (int): Items per page
            message (str): Response message
        
        Returns:
            dict: Formatted paginated response
        """
        total_pages = (total + per_page - 1) // per_page  # Ceiling division
        
        return self.success_response(
            message=message,
            data=data,
            meta={
                'pagination': {
                    'current_page': page,
                    'per_page': per_page,
                    'total_items': total,
                    'total_pages': total_pages,
                    'has_next': page < total_pages,
                    'has_prev': page > 1
                }
            }
        )
    
    
    def file_upload_response(self, filename: str, file_size: int, upload_id: str, 
                           message: str = "File uploaded successfully") -> Dict[str, Any]:
        """
        Format file upload response
        
        Args:
            filename (str): Uploaded filename
            file_size (int): File size in bytes
            upload_id (str): Unique upload identifier
            message (str): Response message
        
        Returns:
            dict: Formatted file upload response
        """
        return self.success_response(
            message=message,
            data={
                'upload_id': upload_id,
                'filename': filename,
                'file_size': file_size,
                'file_size_mb': round(file_size / 1024 / 1024, 2)
            }
        )
    
    
    def processing_response(self, task_id: str, status: str, progress: Optional[float] = None,
                          message: str = "Processing in progress") -> Dict[str, Any]:
        """
        Format processing status response
        
        Args:
            task_id (str): Task identifier
            status (str): Processing status
            progress (float): Progress percentage (0-100)
            message (str): Response message
        
        Returns:
            dict: Formatted processing response
        """
        data = {
            'task_id': task_id,
            'status': status
        }
        
        if progress is not None:
            data['progress'] = min(100, max(0, progress))  # Clamp between 0-100
        
        return self.success_response(
            message=message,
            data=data
        )
    
    
    def batch_response(self, results: list, successful: int, failed: int, 
                      total: int, batch_id: str, 
                      message: str = "Batch processing completed") -> Dict[str, Any]:
        """
        Format batch processing response
        
        Args:
            results (list): List of individual results
            successful (int): Number of successful operations
            failed (int): Number of failed operations
            total (int): Total number of operations
            batch_id (str): Batch identifier
            message (str): Response message
        
        Returns:
            dict: Formatted batch response
        """
        success_rate = (successful / total * 100) if total > 0 else 0
        
        return self.success_response(
            message=message,
            data={
                'batch_id': batch_id,
                'summary': {
                    'total': total,
                    'successful': successful,
                    'failed': failed,
                    'success_rate': round(success_rate, 2)
                },
                'results': results
            }
        )
    
    
    def format_response(self, success: bool, message: str, data: Optional[Any] = None, 
                       status_code: int = 200, **kwargs) -> Dict[str, Any]:
        """
        Generic response formatter
        
        Args:
            success (bool): Whether operation was successful
            message (str): Response message
            data (any): Response data
            status_code (int): HTTP status code
            **kwargs: Additional fields to include
        
        Returns:
            dict: Formatted response
        """
        response = {
            'success': success,
            'message': message,
            'status_code': status_code,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if data is not None:
            response['data'] = data
        
        # Add any additional fields
        for key, value in kwargs.items():
            if key not in response:  # Don't override core fields
                response[key] = value
        
        return response
    
    
    def api_info_response(self, service_name: str, version: str, description: str, 
                         endpoints: Dict[str, str], **kwargs) -> Dict[str, Any]:
        """
        Format API information response
        
        Args:
            service_name (str): API service name
            version (str): API version
            description (str): API description
            endpoints (dict): Available endpoints
            **kwargs: Additional API information
        
        Returns:
            dict: Formatted API info response
        """
        data = {
            'service': service_name,
            'version': version,
            'description': description,
            'endpoints': endpoints,
            'server_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Add any additional info
        data.update(kwargs)
        
        return self.success_response(
            message="API information retrieved",
            data=data
        )
    
    
    def health_check_response(self, status: str, checks: Dict[str, Any], 
                            uptime: str, response_time: float) -> Dict[str, Any]:
        """
        Format health check response
        
        Args:
            status (str): Overall health status
            checks (dict): Individual health checks
            uptime (str): System uptime
            response_time (float): Response time in ms
        
        Returns:
            dict: Formatted health check response
        """
        data = {
            'status': status,
            'uptime': uptime,
            'response_time_ms': response_time,
            'checks': checks
        }
        
        success = status in ['healthy', 'warning']
        status_code = 200 if success else 503
        
        return self.format_response(
            success=success,
            message=f"System is {status}",
            data=data,
            status_code=status_code
        )
