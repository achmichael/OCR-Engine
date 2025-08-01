"""
Health Controller
================

Controller untuk health checks dan system monitoring.

Author: AI Assistant
Date: August 2025
"""

import os
import time
import psutil
from typing import Dict, Any
from flask import current_app
import importlib.util

from app.utils.response_formatter import ResponseFormatter


class HealthController:
    """
    Controller untuk system health checks
    
    Menangani:
    - Basic health status
    - System resource monitoring
    - Dependency checks
    - Performance metrics
    """
    
    def __init__(self):
        """Initialize Health Controller"""
        self.response_formatter = ResponseFormatter()
    
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system health status
        
        Returns:
            dict: Complete health check results
        """
        try:
            start_time = time.time()
            
            # Basic health info
            health_data = {
                'status': 'healthy',
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'uptime': self._get_uptime(),
                'service_info': {
                    'name': current_app.config.get('API_TITLE', 'OCR ML Engine API'),
                    'version': current_app.config.get('API_VERSION', '1.0.0'),
                    'environment': current_app.config.get('ENV', 'development')
                }
            }
            
            # System resources
            health_data['system'] = self._get_system_metrics()
            
            # Dependency checks
            dependencies = self._check_dependencies()
            health_data['dependencies'] = dependencies
            
            # Storage checks
            health_data['storage'] = self._check_storage()
            
            # Determine overall health status
            overall_status = self._determine_overall_status(dependencies, health_data['system'])
            health_data['status'] = overall_status
            
            # Response time
            health_data['response_time'] = round((time.time() - start_time) * 1000, 2)
            
            status_code = 200 if overall_status == 'healthy' else 503
            
            return self.response_formatter.format_response(
                success=overall_status == 'healthy',
                message=f'System is {overall_status}',
                data=health_data,
                status_code=status_code
            )
            
        except Exception as e:
            current_app.logger.error(f"Health check failed: {e}")
            return self.response_formatter.error_response(
                'Health check failed',
                str(e),
                status_code=503
            )
    
    
    def _get_uptime(self) -> str:
        """
        Get application uptime
        
        Returns:
            str: Uptime formatted string
        """
        try:
            # Simple uptime based on process start time
            process = psutil.Process()
            create_time = process.create_time()
            uptime_seconds = time.time() - create_time
            
            # Convert ke human readable format
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            if days > 0:
                return f"{days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"
                
        except Exception:
            return "unknown"
    
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """
        Get system resource metrics
        
        Returns:
            dict: System metrics data
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage for current directory
            disk = psutil.disk_usage('.')
            
            return {
                'cpu': {
                    'usage_percent': cpu_percent,
                    'cores': psutil.cpu_count(),
                    'status': 'healthy' if cpu_percent < 80 else 'warning' if cpu_percent < 95 else 'critical'
                },
                'memory': {
                    'total_mb': round(memory.total / 1024 / 1024, 2),
                    'used_mb': round(memory.used / 1024 / 1024, 2),
                    'available_mb': round(memory.available / 1024 / 1024, 2),
                    'usage_percent': memory.percent,
                    'status': 'healthy' if memory.percent < 80 else 'warning' if memory.percent < 95 else 'critical'
                },
                'disk': {
                    'total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
                    'used_gb': round(disk.used / 1024 / 1024 / 1024, 2),
                    'free_gb': round(disk.free / 1024 / 1024 / 1024, 2),
                    'usage_percent': round((disk.used / disk.total) * 100, 2),
                    'status': 'healthy' if disk.used / disk.total < 0.8 else 'warning' if disk.used / disk.total < 0.95 else 'critical'
                }
            }
            
        except Exception as e:
            return {
                'error': f'Failed to get system metrics: {e}',
                'status': 'error'
            }
    
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """
        Check availability of required dependencies
        
        Returns:
            dict: Dependency check results
        """
        dependencies = {}
        
        # Critical dependencies
        critical_deps = {
            'opencv-python': 'cv2',
            'Pillow': 'PIL',
            'numpy': 'numpy',
            'flask': 'flask',
            'pytesseract': 'pytesseract',
            'easyocr': 'easyocr',
            'pdf2image': 'pdf2image',
            'PyPDF2': 'PyPDF2'
        }
        
        for dep_name, import_name in critical_deps.items():
            try:
                spec = importlib.util.find_spec(import_name)
                if spec is not None:
                    # Try to import untuk version info
                    module = importlib.import_module(import_name)
                    version = getattr(module, '__version__', 'unknown')
                    
                    dependencies[dep_name] = {
                        'status': 'available',
                        'version': version,
                        'critical': True
                    }
                else:
                    dependencies[dep_name] = {
                        'status': 'missing',
                        'version': None,
                        'critical': True,
                        'error': 'Module not found'
                    }
                    
            except Exception as e:
                dependencies[dep_name] = {
                    'status': 'error',
                    'version': None,
                    'critical': True,
                    'error': str(e)
                }
        
        # Optional dependencies
        optional_deps = {
            'psutil': 'psutil',
            'requests': 'requests'
        }
        
        for dep_name, import_name in optional_deps.items():
            try:
                spec = importlib.util.find_spec(import_name)
                if spec is not None:
                    module = importlib.import_module(import_name)
                    version = getattr(module, '__version__', 'unknown')
                    
                    dependencies[dep_name] = {
                        'status': 'available',
                        'version': version,
                        'critical': False
                    }
                else:
                    dependencies[dep_name] = {
                        'status': 'missing',
                        'version': None,
                        'critical': False
                    }
                    
            except Exception as e:
                dependencies[dep_name] = {
                    'status': 'error',
                    'version': None,
                    'critical': False,
                    'error': str(e)
                }
        
        return dependencies
    
    
    def _check_storage(self) -> Dict[str, Any]:
        """
        Check storage availability dan configuration
        
        Returns:
            dict: Storage check results
        """
        try:
            storage_info = {
                'temp_directory': {
                    'path': current_app.config.get('UPLOAD_FOLDER', 'temp'),
                    'exists': False,
                    'writable': False
                },
                'results_directory': {
                    'path': current_app.config.get('RESULTS_FOLDER', 'results'),
                    'exists': False,
                    'writable': False
                }
            }
            
            for dir_type, dir_info in storage_info.items():
                path = dir_info['path']
                
                # Check if directory exists
                if os.path.exists(path):
                    dir_info['exists'] = True
                    
                    # Check if writable
                    if os.access(path, os.W_OK):
                        dir_info['writable'] = True
                else:
                    # Try to create directory
                    try:
                        os.makedirs(path, exist_ok=True)
                        dir_info['exists'] = True
                        dir_info['writable'] = True
                    except Exception as e:
                        dir_info['error'] = str(e)
            
            return storage_info
            
        except Exception as e:
            return {
                'error': f'Storage check failed: {e}',
                'status': 'error'
            }
    
    
    def _determine_overall_status(self, dependencies: Dict[str, Any], system: Dict[str, Any]) -> str:
        """
        Determine overall system health status
        
        Args:
            dependencies (dict): Dependency check results
            system (dict): System metrics
        
        Returns:
            str: Overall status ('healthy', 'warning', 'critical')
        """
        # Check critical dependencies
        critical_deps_failed = any(
            dep.get('status') != 'available' and dep.get('critical', False) 
            for dep in dependencies.values()
        )
        
        if critical_deps_failed:
            return 'critical'
        
        # Check system resources
        if system.get('error'):
            return 'warning'
        
        cpu_status = system.get('cpu', {}).get('status', 'healthy')
        memory_status = system.get('memory', {}).get('status', 'healthy')
        disk_status = system.get('disk', {}).get('status', 'healthy')
        
        if any(status == 'critical' for status in [cpu_status, memory_status, disk_status]):
            return 'critical'
        
        if any(status == 'warning' for status in [cpu_status, memory_status, disk_status]):
            return 'warning'
        
        return 'healthy'
