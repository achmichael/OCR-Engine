"""
OCR Controller
==============

Controller untuk menangani semua OCR operations dan business logic.

Author: AI Assistant
Date: August 2025
"""

import os
import uuid
import time
from typing import Dict, List, Any, Optional
from werkzeug.datastructures import FileStorage
from flask import current_app
import io
from PIL import Image
import json

# Import services
from app.services.ocr_service import OCRService
from app.services.pdf_service import PDFService
from app.services.image_service import ImageService
from app.utils.file_manager import FileManager
from app.utils.response_formatter import ResponseFormatter


class OCRController:
    """
    Controller untuk OCR operations
    
    Menangani:
    - Processing single images
    - Batch processing multiple images  
    - PDF text extraction
    - Result management
    - Error handling
    """
    
    def __init__(self):
        """Initialize OCR Controller dengan services"""
        self.ocr_service = None
        self.pdf_service = None
        self.image_service = None
        self.file_manager = None
        self.response_formatter = ResponseFormatter()
        
        # Initialize services saat pertama kali digunakan (lazy loading)
        self._initialized = False
    
    
    def _ensure_initialized(self):
        """Ensure semua services sudah diinisialisasi"""
        if not self._initialized:
            self.ocr_service = OCRService()
            self.pdf_service = PDFService()
            self.image_service = ImageService()
            self.file_manager = FileManager()
            self._initialized = True
    
    
    def process_single_image(self, file: FileStorage, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process single image file untuk OCR
        
        Args:
            file (FileStorage): Image file dari request
            params (dict): Processing parameters
                - enhancement_level: int (1-3)
                - engine: str ('tesseract', 'easyocr', 'both')
                - languages: str (comma-separated language codes)
        
        Returns:
            dict: OCR result dengan extracted text dan metadata
        """
        try:
            self._ensure_initialized()
            
            # Generate unique result ID
            result_id = str(uuid.uuid4())
            
            # Save uploaded file temporarily
            temp_path = self.file_manager.save_temp_file(file, result_id)
            
            try:
                # Load dan validate image
                image = self.image_service.load_image(temp_path)
                if image is None:
                    return self.response_formatter.error_response(
                        'Invalid image file',
                        'Could not load the uploaded image'
                    )
                
                # Apply image enhancement
                enhanced_image = self.image_service.enhance_image(
                    image, 
                    level=params.get('enhancement_level', 2)
                )
                
                # Perform OCR
                ocr_result = self.ocr_service.extract_text(
                    enhanced_image,
                    engine=params.get('engine', 'both'),
                    languages=params.get('languages', 'en,id').split(',')
                )
                
                # Calculate confidence dan statistics
                stats = self._calculate_text_stats(ocr_result.get('text', ''))
                
                # Prepare result
                result = {
                    'result_id': result_id,
                    'filename': file.filename,
                    'file_size': len(file.read()),
                    'processing_time': ocr_result.get('processing_time', 0),
                    'enhancement_level': params.get('enhancement_level', 2),
                    'engine_used': ocr_result.get('engine_used', params.get('engine', 'both')),
                    'languages': params.get('languages', 'en,id').split(','),
                    'extracted_text': ocr_result.get('text', ''),
                    'confidence_score': ocr_result.get('confidence', 0),
                    'statistics': stats,
                    'metadata': {
                        'image_size': f"{image.width}x{image.height}",
                        'image_mode': image.mode,
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'api_version': current_app.config.get('API_VERSION', '1.0.0')
                    }
                }
                
                # Save result untuk future retrieval
                self._save_result(result_id, result)
                
                # Reset file pointer
                file.seek(0)
                
                return self.response_formatter.success_response(
                    'Image processed successfully',
                    result
                )
                
            finally:
                # Cleanup temporary file
                self.file_manager.cleanup_temp_file(temp_path)
                
        except Exception as e:
            current_app.logger.error(f"Single image OCR error: {e}")
            return self.response_formatter.error_response(
                'Processing failed',
                str(e)
            )
    
    
    def process_batch_images(self, files: List[FileStorage], params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process multiple images untuk batch OCR
        
        Args:
            files (list): List of image files
            params (dict): Processing parameters
        
        Returns:
            dict: Batch processing results
        """
        try:
            self._ensure_initialized()
            
            batch_id = str(uuid.uuid4())
            results = []
            successful_count = 0
            failed_count = 0
            total_processing_time = 0
            
            current_app.logger.info(f"Starting batch processing with {len(files)} files")
            
            for i, file in enumerate(files):
                try:
                    # Process each file
                    file_result = self.process_single_image(file, params)
                    
                    if file_result.get('success', False):
                        successful_count += 1
                        total_processing_time += file_result.get('data', {}).get('processing_time', 0)
                        
                        # Add batch info ke result
                        file_result['data']['batch_id'] = batch_id
                        file_result['data']['batch_index'] = i + 1
                        
                    else:
                        failed_count += 1
                    
                    results.append(file_result)
                    
                except Exception as e:
                    failed_count += 1
                    results.append(self.response_formatter.error_response(
                        f'Failed to process {file.filename}',
                        str(e)
                    ))
            
            # Prepare batch summary
            batch_result = {
                'batch_id': batch_id,
                'total_files': len(files),
                'successful': successful_count,
                'failed': failed_count,
                'success_rate': (successful_count / len(files)) * 100 if files else 0,
                'total_processing_time': total_processing_time,
                'average_processing_time': total_processing_time / successful_count if successful_count > 0 else 0,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'results': results
            }
            
            # Save batch result
            self._save_result(batch_id, batch_result)
            
            return self.response_formatter.success_response(
                f'Batch processing completed: {successful_count}/{len(files)} successful',
                batch_result
            )
            
        except Exception as e:
            current_app.logger.error(f"Batch OCR error: {e}")
            return self.response_formatter.error_response(
                'Batch processing failed',
                str(e)
            )
    
    
    def process_pdf_file(self, file: FileStorage, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process PDF file untuk text extraction
        
        Args:
            file (FileStorage): PDF file dari request
            params (dict): Processing parameters
                - page_start: int (optional)
                - page_end: int (optional)
                - enhancement_level: int (1-3)
                - try_direct: bool (try direct text extraction first)
        
        Returns:
            dict: PDF processing result
        """
        try:
            self._ensure_initialized()
            
            result_id = str(uuid.uuid4())
            
            # Save PDF temporarily
            temp_path = self.file_manager.save_temp_file(file, result_id)
            
            try:
                # Get PDF info
                pdf_info = self.pdf_service.get_pdf_info(temp_path)
                
                if not pdf_info:
                    return self.response_formatter.error_response(
                        'Invalid PDF file',
                        'Could not read the uploaded PDF'
                    )
                
                # Extract text dengan parameters
                extraction_result = self.pdf_service.extract_text_from_pdf(
                    temp_path,
                    page_start=params.get('page_start'),
                    page_end=params.get('page_end'),
                    enhancement_level=params.get('enhancement_level', 2),
                    try_direct=params.get('try_direct', True)
                )
                
                # Calculate statistics
                all_text = ' '.join([page.get('text', '') for page in extraction_result.get('pages', [])])
                stats = self._calculate_text_stats(all_text)
                
                # Prepare result
                result = {
                    'result_id': result_id,
                    'filename': file.filename,
                    'file_size': len(file.read()),
                    'pdf_info': pdf_info,
                    'processing_method': extraction_result.get('method', 'unknown'),
                    'pages_processed': len(extraction_result.get('pages', [])),
                    'total_processing_time': extraction_result.get('total_time', 0),
                    'enhancement_level': params.get('enhancement_level', 2),
                    'pages': extraction_result.get('pages', []),
                    'full_text': all_text,
                    'average_confidence': extraction_result.get('average_confidence', 0),
                    'statistics': stats,
                    'metadata': {
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'api_version': current_app.config.get('API_VERSION', '1.0.0')
                    }
                }
                
                # Save result
                self._save_result(result_id, result)
                
                # Reset file pointer
                file.seek(0)
                
                return self.response_formatter.success_response(
                    f'PDF processed successfully: {len(extraction_result.get("pages", []))} pages',
                    result
                )
                
            finally:
                # Cleanup
                self.file_manager.cleanup_temp_file(temp_path)
                
        except Exception as e:
            current_app.logger.error(f"PDF OCR error: {e}")
            return self.response_formatter.error_response(
                'PDF processing failed',
                str(e)
            )
    
    
    def get_result_by_id(self, result_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve OCR result berdasarkan ID
        
        Args:
            result_id (str): Result ID
        
        Returns:
            dict: Stored result data atau None jika tidak ditemukan
        """
        try:
            self._ensure_initialized()
            return self.file_manager.load_result(result_id)
            
        except Exception as e:
            current_app.logger.error(f"Failed to retrieve result {result_id}: {e}")
            return None
    
    
    def get_models_info(self) -> Dict[str, Any]:
        """
        Get information tentang available OCR models
        
        Returns:
            dict: Models information
        """
        try:
            self._ensure_initialized()
            
            tesseract_info = self.ocr_service.get_tesseract_info()
            easyocr_info = self.ocr_service.get_easyocr_info()
            
            return self.response_formatter.success_response(
                'Models information retrieved',
                {
                    'tesseract': tesseract_info,
                    'easyocr': easyocr_info,
                    'supported_languages': self.ocr_service.get_supported_languages(),
                    'default_engine': current_app.config.get('OCR_DEFAULT_ENGINE', 'both'),
                    'available_engines': ['tesseract', 'easyocr', 'both']
                }
            )
            
        except Exception as e:
            current_app.logger.error(f"Failed to get models info: {e}")
            return self.response_formatter.error_response(
                'Failed to get models information',
                str(e)
            )
    
    
    def _calculate_text_stats(self, text: str) -> Dict[str, Any]:
        """
        Calculate text statistics
        
        Args:
            text (str): Extracted text
        
        Returns:
            dict: Text statistics
        """
        if not text:
            return {
                'character_count': 0,
                'word_count': 0,
                'line_count': 0,
                'paragraph_count': 0,
                'has_numbers': False,
                'has_special_chars': False
            }
        
        import re
        
        # Basic counts
        char_count = len(text)
        word_count = len(text.split())
        line_count = len(text.split('\n'))
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        # Content analysis
        has_numbers = bool(re.search(r'\d', text))
        has_special_chars = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', text))
        
        return {
            'character_count': char_count,
            'word_count': word_count,
            'line_count': line_count,
            'paragraph_count': paragraph_count,
            'has_numbers': has_numbers,
            'has_special_chars': has_special_chars
        }
    
    
    def _save_result(self, result_id: str, result_data: Dict[str, Any]) -> None:
        """
        Save result ke storage untuk future retrieval
        
        Args:
            result_id (str): Unique result ID
            result_data (dict): Result data untuk disimpan
        """
        try:
            self.file_manager.save_result(result_id, result_data)
            
        except Exception as e:
            current_app.logger.error(f"Failed to save result {result_id}: {e}")
            # Don't raise error, just log it
