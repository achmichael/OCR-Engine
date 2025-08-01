"""
PDF Service
===========

Service untuk PDF processing dan text extraction.

Author: AI Assistant
Date: August 2025
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
import tempfile
import os
from pathlib import Path

# PDF processing imports
try:
    import PyPDF2
    from pdf2image import convert_from_path
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

from PIL import Image
import numpy as np

# Import internal services
from app.services.image_service import ImageService
from app.services.ocr_service import OCRService


class PDFService:
    """
    Service untuk PDF processing operations
    
    Features:
    - Direct text extraction dari PDF
    - Image conversion dan OCR fallback
    - Page-by-page processing
    - Batch processing support
    """
    
    def __init__(self):
        """Initialize PDF Service"""
        self.logger = logging.getLogger(__name__)
        self.image_service = ImageService()
        self.ocr_service = OCRService()
        
        # Check dependencies
        if not DEPENDENCIES_AVAILABLE:
            self.logger.warning("PDF dependencies not available. Limited functionality.")
        
        # PDF processing configuration
        self.config = {
            'dpi': 300,  # DPI untuk PDF to image conversion
            'format': 'PNG',  # Output format untuk converted images
            'thread_count': 1,  # Parallel processing threads
            'max_pages': 100,  # Maximum pages to process
            'direct_extraction_threshold': 0.1  # Minimum text ratio untuk direct extraction
        }
    
    
    def get_pdf_info(self, pdf_path: str) -> Optional[Dict[str, Any]]:
        """
        Get basic information tentang PDF file
        
        Args:
            pdf_path (str): Path ke PDF file
        
        Returns:
            dict: PDF information atau None jika gagal
        """
        try:
            if not DEPENDENCIES_AVAILABLE:
                return None
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Get basic info
                num_pages = len(pdf_reader.pages)
                
                # Try to get metadata
                metadata = {}
                if pdf_reader.metadata:
                    for key, value in pdf_reader.metadata.items():
                        if value:
                            metadata[key.replace('/', '')] = str(value)
                
                # Check if PDF has extractable text
                extractable_text = False
                sample_text = ""
                
                if num_pages > 0:
                    try:
                        first_page = pdf_reader.pages[0]
                        sample_text = first_page.extract_text()
                        extractable_text = len(sample_text.strip()) > 0
                    except Exception:
                        pass
                
                return {
                    'filename': os.path.basename(pdf_path),
                    'file_size': os.path.getsize(pdf_path),
                    'page_count': num_pages,
                    'has_extractable_text': extractable_text,
                    'sample_text_length': len(sample_text.strip()),
                    'metadata': metadata,
                    'processing_recommendation': 'direct' if extractable_text else 'ocr'
                }
                
        except Exception as e:
            self.logger.error(f"Failed to get PDF info for {pdf_path}: {e}")
            return None
    
    
    def extract_text_from_pdf(self, pdf_path: str, page_start: Optional[int] = None,
                             page_end: Optional[int] = None, enhancement_level: int = 2,
                             try_direct: bool = True) -> Dict[str, Any]:
        """
        Extract text dari PDF menggunakan direct extraction atau OCR
        
        Args:
            pdf_path (str): Path ke PDF file
            page_start (int): Starting page (1-indexed, optional)
            page_end (int): Ending page (1-indexed, optional)
            enhancement_level (int): Image enhancement level untuk OCR
            try_direct (bool): Try direct text extraction first
        
        Returns:
            dict: Extraction result dengan pages dan metadata
        """
        start_time = time.time()
        
        try:
            if not DEPENDENCIES_AVAILABLE:
                return {
                    'pages': [],
                    'method': 'error',
                    'total_time': time.time() - start_time,
                    'error': 'PDF dependencies not available'
                }
            
            # Get PDF info
            pdf_info = self.get_pdf_info(pdf_path)
            if not pdf_info:
                return {
                    'pages': [],
                    'method': 'error',
                    'total_time': time.time() - start_time,
                    'error': 'Failed to read PDF'
                }
            
            total_pages = pdf_info['page_count']
            
            # Determine page range
            if page_start is None:
                page_start = 1
            if page_end is None:
                page_end = total_pages
            
            # Validate page range
            page_start = max(1, min(page_start, total_pages))
            page_end = max(page_start, min(page_end, total_pages))
            
            # Limit pages untuk performance
            if page_end - page_start + 1 > self.config['max_pages']:
                page_end = page_start + self.config['max_pages'] - 1
                self.logger.warning(f"Limited processing to {self.config['max_pages']} pages")
            
            # Try direct extraction first jika enabled
            if try_direct and pdf_info['has_extractable_text']:
                direct_result = self._extract_direct_text(pdf_path, page_start, page_end)
                
                # Check quality of direct extraction
                if self._is_direct_extraction_good(direct_result):
                    direct_result['method'] = 'direct'
                    direct_result['total_time'] = time.time() - start_time
                    return direct_result
                else:
                    self.logger.info("Direct extraction quality poor, falling back to OCR")
            
            # Fallback ke OCR extraction
            ocr_result = self._extract_with_ocr(pdf_path, page_start, page_end, enhancement_level)
            ocr_result['method'] = 'ocr'
            ocr_result['total_time'] = time.time() - start_time
            
            return ocr_result
            
        except Exception as e:
            self.logger.error(f"PDF text extraction failed: {e}")
            return {
                'pages': [],
                'method': 'error',
                'total_time': time.time() - start_time,
                'error': str(e)
            }
    
    
    def _extract_direct_text(self, pdf_path: str, page_start: int, page_end: int) -> Dict[str, Any]:
        """
        Extract text directly dari PDF menggunakan PyPDF2
        
        Args:
            pdf_path (str): Path ke PDF file
            page_start (int): Starting page
            page_end (int): Ending page
        
        Returns:
            dict: Direct extraction result
        """
        try:
            pages = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(page_start - 1, page_end):
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        pages.append({
                            'page_number': page_num + 1,
                            'text': text.strip(),
                            'extraction_method': 'direct',
                            'confidence': 100 if text.strip() else 0,
                            'word_count': len(text.split()) if text else 0
                        })
                        
                    except Exception as e:
                        self.logger.error(f"Failed to extract page {page_num + 1}: {e}")
                        pages.append({
                            'page_number': page_num + 1,
                            'text': '',
                            'extraction_method': 'direct',
                            'confidence': 0,
                            'word_count': 0,
                            'error': str(e)
                        })
            
            # Calculate average confidence
            confidences = [p['confidence'] for p in pages if p['confidence'] > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'pages': pages,
                'average_confidence': avg_confidence,
                'pages_processed': len(pages)
            }
            
        except Exception as e:
            self.logger.error(f"Direct text extraction failed: {e}")
            return {
                'pages': [],
                'average_confidence': 0,
                'pages_processed': 0,
                'error': str(e)
            }
    
    
    def _extract_with_ocr(self, pdf_path: str, page_start: int, page_end: int, 
                         enhancement_level: int) -> Dict[str, Any]:
        """
        Extract text menggunakan OCR pada converted images
        
        Args:
            pdf_path (str): Path ke PDF file
            page_start (int): Starting page
            page_end (int): Ending page
            enhancement_level (int): Image enhancement level
        
        Returns:
            dict: OCR extraction result
        """
        try:
            pages = []
            
            # Convert PDF pages ke images
            images = convert_from_path(
                pdf_path,
                dpi=self.config['dpi'],
                first_page=page_start,
                last_page=page_end,
                fmt=self.config['format']
            )
            
            for i, image in enumerate(images):
                page_num = page_start + i
                
                try:
                    # Apply image enhancement
                    enhanced_image = self.image_service.enhance_image(image, enhancement_level)
                    
                    # Perform OCR
                    ocr_result = self.ocr_service.extract_text(enhanced_image)
                    
                    pages.append({
                        'page_number': page_num,
                        'text': ocr_result.get('text', ''),
                        'extraction_method': 'ocr',
                        'confidence': ocr_result.get('confidence', 0),
                        'word_count': len(ocr_result.get('text', '').split()) if ocr_result.get('text') else 0,
                        'engine_used': ocr_result.get('engine_used', 'unknown'),
                        'processing_time': ocr_result.get('processing_time', 0)
                    })
                    
                except Exception as e:
                    self.logger.error(f"OCR failed for page {page_num}: {e}")
                    pages.append({
                        'page_number': page_num,
                        'text': '',
                        'extraction_method': 'ocr',
                        'confidence': 0,
                        'word_count': 0,
                        'error': str(e)
                    })
            
            # Calculate statistics
            confidences = [p['confidence'] for p in pages if p['confidence'] > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            processing_times = [p.get('processing_time', 0) for p in pages]
            total_processing_time = sum(processing_times)
            
            return {
                'pages': pages,
                'average_confidence': avg_confidence,
                'pages_processed': len(pages),
                'total_ocr_time': total_processing_time
            }
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return {
                'pages': [],
                'average_confidence': 0,
                'pages_processed': 0,
                'error': str(e)
            }
    
    
    def _is_direct_extraction_good(self, extraction_result: Dict[str, Any]) -> bool:
        """
        Evaluate quality dari direct text extraction
        
        Args:
            extraction_result (dict): Direct extraction result
        
        Returns:
            bool: True jika extraction quality good
        """
        try:
            pages = extraction_result.get('pages', [])
            if not pages:
                return False
            
            # Calculate text density
            total_chars = sum(len(p.get('text', '')) for p in pages)
            pages_with_text = sum(1 for p in pages if len(p.get('text', '').strip()) > 0)
            
            # Quality criteria
            text_density = total_chars / len(pages) if pages else 0
            coverage = pages_with_text / len(pages) if pages else 0
            
            # Good extraction criteria:
            # - At least 50 characters per page on average
            # - At least 70% pages have text
            # - No extraction errors
            has_errors = any('error' in p for p in pages)
            
            is_good = (
                text_density >= 50 and
                coverage >= 0.7 and
                not has_errors
            )
            
            self.logger.info(f"Direct extraction quality: density={text_density:.1f}, "
                           f"coverage={coverage:.2%}, errors={has_errors}, good={is_good}")
            
            return is_good
            
        except Exception as e:
            self.logger.error(f"Failed to evaluate extraction quality: {e}")
            return False
    
    
    def convert_pdf_to_images(self, pdf_path: str, output_dir: str, 
                             page_start: Optional[int] = None, 
                             page_end: Optional[int] = None) -> Dict[str, Any]:
        """
        Convert PDF pages ke individual image files
        
        Args:
            pdf_path (str): Path ke PDF file
            output_dir (str): Directory untuk save images
            page_start (int): Starting page (optional)
            page_end (int): Ending page (optional)
        
        Returns:
            dict: Conversion result dengan image paths
        """
        try:
            if not DEPENDENCIES_AVAILABLE:
                return {
                    'success': False,
                    'error': 'PDF dependencies not available',
                    'images': []
                }
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Get PDF info untuk page validation
            pdf_info = self.get_pdf_info(pdf_path)
            if not pdf_info:
                return {
                    'success': False,
                    'error': 'Failed to read PDF',
                    'images': []
                }
            
            total_pages = pdf_info['page_count']
            
            # Set default page range
            if page_start is None:
                page_start = 1
            if page_end is None:
                page_end = total_pages
            
            # Convert pages
            images = convert_from_path(
                pdf_path,
                dpi=self.config['dpi'],
                first_page=page_start,
                last_page=page_end,
                fmt=self.config['format']
            )
            
            # Save images
            saved_images = []
            base_name = Path(pdf_path).stem
            
            for i, image in enumerate(images):
                page_num = page_start + i
                image_filename = f"{base_name}_page_{page_num:03d}.{self.config['format'].lower()}"
                image_path = os.path.join(output_dir, image_filename)
                
                image.save(image_path, self.config['format'])
                saved_images.append({
                    'page_number': page_num,
                    'image_path': image_path,
                    'image_size': image.size
                })
            
            return {
                'success': True,
                'images': saved_images,
                'total_pages_converted': len(saved_images),
                'output_directory': output_dir
            }
            
        except Exception as e:
            self.logger.error(f"PDF to images conversion failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'images': []
            }
    
    
    def get_text_from_page_range(self, pdf_path: str, pages: List[int], 
                                enhancement_level: int = 2) -> Dict[str, Any]:
        """
        Extract text dari specific pages
        
        Args:
            pdf_path (str): Path ke PDF file
            pages (list): List of page numbers to extract
            enhancement_level (int): Enhancement level untuk OCR
        
        Returns:
            dict: Extraction result
        """
        try:
            results = []
            
            for page_num in pages:
                # Extract single page
                result = self.extract_text_from_pdf(
                    pdf_path,
                    page_start=page_num,
                    page_end=page_num,
                    enhancement_level=enhancement_level
                )
                
                if result.get('pages'):
                    results.extend(result['pages'])
            
            # Calculate aggregate statistics
            if results:
                confidences = [p['confidence'] for p in results if p['confidence'] > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                return {
                    'success': True,
                    'pages': results,
                    'pages_processed': len(results),
                    'average_confidence': avg_confidence
                }
            else:
                return {
                    'success': False,
                    'pages': [],
                    'pages_processed': 0,
                    'error': 'No pages successfully processed'
                }
                
        except Exception as e:
            self.logger.error(f"Page range extraction failed: {e}")
            return {
                'success': False,
                'pages': [],
                'pages_processed': 0,
                'error': str(e)
            }
