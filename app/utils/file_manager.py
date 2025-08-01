"""
File Manager
============

Utility untuk file operations dan temporary file management.

Author: AI Assistant
Date: August 2025
"""

import os
import json
import uuid
import shutil
import tempfile
from typing import Dict, Any, Optional
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import time
from pathlib import Path


class FileManager:
    """
    Class untuk managing file operations
    
    Handles:
    - Temporary file storage
    - Result data persistence
    - File cleanup
    - Directory management
    """
    
    def __init__(self, base_temp_dir: str = None, base_results_dir: str = None):
        """
        Initialize FileManager
        
        Args:
            base_temp_dir (str): Base directory untuk temporary files
            base_results_dir (str): Base directory untuk results storage
        """
        self.base_temp_dir = base_temp_dir or os.path.join(tempfile.gettempdir(), 'ocr_engine')
        self.base_results_dir = base_results_dir or os.path.join(os.getcwd(), 'results')
        
        # Ensure directories exist
        self._ensure_directories()
    
    
    def _ensure_directories(self):
        """Create necessary directories jika belum ada"""
        try:
            os.makedirs(self.base_temp_dir, exist_ok=True)
            os.makedirs(self.base_results_dir, exist_ok=True)
            
            # Create subdirectories
            for subdir in ['uploads', 'processed', 'cache']:
                os.makedirs(os.path.join(self.base_temp_dir, subdir), exist_ok=True)
            
            for subdir in ['ocr_results', 'batch_results', 'pdf_results']:
                os.makedirs(os.path.join(self.base_results_dir, subdir), exist_ok=True)
                
        except Exception as e:
            raise Exception(f"Failed to create directories: {e}")
    
    
    def save_temp_file(self, file: FileStorage, identifier: str) -> str:
        """
        Save uploaded file ke temporary location
        
        Args:
            file (FileStorage): Uploaded file
            identifier (str): Unique identifier untuk filename
        
        Returns:
            str: Path ke saved temporary file
        """
        try:
            # Sanitize filename
            original_filename = secure_filename(file.filename)
            if not original_filename:
                original_filename = 'uploaded_file'
            
            # Create unique filename dengan identifier
            name, ext = os.path.splitext(original_filename)
            temp_filename = f"{identifier}_{name}{ext}"
            
            # Full path
            temp_path = os.path.join(self.base_temp_dir, 'uploads', temp_filename)
            
            # Save file
            file.save(temp_path)
            
            return temp_path
            
        except Exception as e:
            raise Exception(f"Failed to save temporary file: {e}")
    
    
    def save_processed_file(self, source_path: str, identifier: str, suffix: str = 'processed') -> str:
        """
        Save processed file ke processed directory
        
        Args:
            source_path (str): Path ke source file
            identifier (str): Unique identifier
            suffix (str): Suffix untuk processed filename
        
        Returns:
            str: Path ke saved processed file
        """
        try:
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            # Get original filename dan extension
            original_name = os.path.basename(source_path)
            name, ext = os.path.splitext(original_name)
            
            # Create processed filename
            processed_filename = f"{identifier}_{suffix}{ext}"
            processed_path = os.path.join(self.base_temp_dir, 'processed', processed_filename)
            
            # Copy file
            shutil.copy2(source_path, processed_path)
            
            return processed_path
            
        except Exception as e:
            raise Exception(f"Failed to save processed file: {e}")
    
    
    def save_result(self, result_id: str, result_data: Dict[str, Any], result_type: str = 'ocr') -> str:
        """
        Save OCR result data ke persistent storage
        
        Args:
            result_id (str): Unique result identifier
            result_data (dict): Result data to save
            result_type (str): Type of result ('ocr', 'batch', 'pdf')
        
        Returns:
            str: Path ke saved result file
        """
        try:
            # Determine subdirectory based on result type
            subdir_map = {
                'ocr': 'ocr_results',
                'batch': 'batch_results', 
                'pdf': 'pdf_results'
            }
            
            subdir = subdir_map.get(result_type, 'ocr_results')
            result_dir = os.path.join(self.base_results_dir, subdir)
            
            # Create result filename
            result_filename = f"{result_id}.json"
            result_path = os.path.join(result_dir, result_filename)
            
            # Add save metadata ke result data
            result_data['_metadata'] = {
                'saved_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'result_id': result_id,
                'result_type': result_type,
                'file_path': result_path
            }
            
            # Save sebagai JSON
            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, indent=2, ensure_ascii=False)
            
            return result_path
            
        except Exception as e:
            raise Exception(f"Failed to save result: {e}")
    
    
    def load_result(self, result_id: str) -> Optional[Dict[str, Any]]:
        """
        Load saved result data berdasarkan ID
        
        Args:
            result_id (str): Result identifier
        
        Returns:
            dict: Loaded result data atau None jika tidak ditemukan
        """
        try:
            # Search di semua result subdirectories
            for subdir in ['ocr_results', 'batch_results', 'pdf_results']:
                result_path = os.path.join(self.base_results_dir, subdir, f"{result_id}.json")
                
                if os.path.exists(result_path):
                    with open(result_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
            
            return None
            
        except Exception as e:
            raise Exception(f"Failed to load result {result_id}: {e}")
    
    
    def cleanup_temp_file(self, file_path: str) -> bool:
        """
        Remove temporary file
        
        Args:
            file_path (str): Path ke file yang akan dihapus
        
        Returns:
            bool: True jika berhasil dihapus
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
            
        except Exception:
            return False
    
    
    def cleanup_old_temp_files(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """
        Cleanup temporary files yang sudah lama
        
        Args:
            max_age_hours (int): Maximum age dalam hours sebelum file dihapus
        
        Returns:
            dict: Cleanup statistics
        """
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            deleted_count = 0
            total_size = 0
            errors = []
            
            # Cleanup uploads directory
            uploads_dir = os.path.join(self.base_temp_dir, 'uploads')
            if os.path.exists(uploads_dir):
                for filename in os.listdir(uploads_dir):
                    file_path = os.path.join(uploads_dir, filename)
                    
                    try:
                        file_age = current_time - os.path.getmtime(file_path)
                        
                        if file_age > max_age_seconds:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            deleted_count += 1
                            total_size += file_size
                            
                    except Exception as e:
                        errors.append(f"Failed to delete {filename}: {e}")
            
            # Cleanup processed directory
            processed_dir = os.path.join(self.base_temp_dir, 'processed')
            if os.path.exists(processed_dir):
                for filename in os.listdir(processed_dir):
                    file_path = os.path.join(processed_dir, filename)
                    
                    try:
                        file_age = current_time - os.path.getmtime(file_path)
                        
                        if file_age > max_age_seconds:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            deleted_count += 1
                            total_size += file_size
                            
                    except Exception as e:
                        errors.append(f"Failed to delete {filename}: {e}")
            
            return {
                'deleted_files': deleted_count,
                'freed_space_bytes': total_size,
                'freed_space_mb': round(total_size / 1024 / 1024, 2),
                'errors': errors,
                'max_age_hours': max_age_hours
            }
            
        except Exception as e:
            return {
                'deleted_files': 0,
                'freed_space_bytes': 0,
                'freed_space_mb': 0,
                'errors': [f"Cleanup failed: {e}"],
                'max_age_hours': max_age_hours
            }
    
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage usage information
        
        Returns:
            dict: Storage information
        """
        try:
            def get_dir_size(path: str) -> int:
                """Get total size of directory"""
                total = 0
                try:
                    for dirpath, dirnames, filenames in os.walk(path):
                        for filename in filenames:
                            file_path = os.path.join(dirpath, filename)
                            try:
                                total += os.path.getsize(file_path)
                            except (OSError, FileNotFoundError):
                                pass
                except Exception:
                    pass
                return total
            
            def count_files(path: str) -> int:
                """Count files dalam directory"""
                count = 0
                try:
                    for dirpath, dirnames, filenames in os.walk(path):
                        count += len(filenames)
                except Exception:
                    pass
                return count
            
            # Get temp directory info
            temp_size = get_dir_size(self.base_temp_dir)
            temp_files = count_files(self.base_temp_dir)
            
            # Get results directory info
            results_size = get_dir_size(self.base_results_dir)
            results_files = count_files(self.base_results_dir)
            
            return {
                'temporary_storage': {
                    'path': self.base_temp_dir,
                    'size_bytes': temp_size,
                    'size_mb': round(temp_size / 1024 / 1024, 2),
                    'file_count': temp_files,
                    'exists': os.path.exists(self.base_temp_dir)
                },
                'results_storage': {
                    'path': self.base_results_dir,
                    'size_bytes': results_size,
                    'size_mb': round(results_size / 1024 / 1024, 2),
                    'file_count': results_files,
                    'exists': os.path.exists(self.base_results_dir)
                },
                'total_storage': {
                    'size_bytes': temp_size + results_size,
                    'size_mb': round((temp_size + results_size) / 1024 / 1024, 2),
                    'file_count': temp_files + results_files
                }
            }
            
        except Exception as e:
            return {
                'error': f"Failed to get storage info: {e}",
                'temporary_storage': {'error': str(e)},
                'results_storage': {'error': str(e)},
                'total_storage': {'error': str(e)}
            }
    
    
    def create_backup(self, backup_name: str = None) -> Dict[str, Any]:
        """
        Create backup dari results directory
        
        Args:
            backup_name (str): Custom backup name
        
        Returns:
            dict: Backup information
        """
        try:
            if not backup_name:
                backup_name = f"ocr_backup_{time.strftime('%Y%m%d_%H%M%S')}"
            
            backup_path = os.path.join(os.getcwd(), f"{backup_name}.zip")
            
            # Create zip archive
            import zipfile
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.base_results_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, self.base_results_dir)
                        zipf.write(file_path, arc_name)
            
            backup_size = os.path.getsize(backup_path)
            
            return {
                'backup_created': True,
                'backup_path': backup_path,
                'backup_size_bytes': backup_size,
                'backup_size_mb': round(backup_size / 1024 / 1024, 2),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            return {
                'backup_created': False,
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
