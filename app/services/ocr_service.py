"""
OCR Service
===========

Core service untuk OCR operations menggunakan multiple engines.

Author: AI Assistant  
Date: August 2025
"""

import time
import logging
from typing import Dict, Any, List, Optional, Union, Tuple
import cv2
import numpy as np
from PIL import Image
import pytesseract
import easyocr
from concurrent.futures import ThreadPoolExecutor, as_completed
import os


class OCRService:
    """
    Service untuk OCR text extraction
    
    Features:
    - Multiple OCR engines (Tesseract, EasyOCR)
    - Parallel processing
    - Confidence scoring
    - Language support
    - Best result selection
    """
    
    def __init__(self):
        """Initialize OCR Service dengan engine configuration"""
        self.logger = logging.getLogger(__name__)
        
        # Engine availability flags
        self._tesseract_available = None
        self._easyocr_available = None
        self._easyocr_reader = None
        
        # Default configuration
        self.default_config = {
            'tesseract_config': '--oem 3 --psm 6',
            'easyocr_gpu': False,
            'confidence_threshold': 0.5,
            'max_workers': 2
        }
        
        # Check engine availability
        self._check_engines()
    
    
    def _check_engines(self):
        """Check availability of OCR engines"""
        # Check Tesseract
        try:
            pytesseract.get_tesseract_version()
            self._tesseract_available = True
            self.logger.info("Tesseract OCR is available")
        except Exception as e:
            self._tesseract_available = False
            self.logger.warning(f"Tesseract OCR not available: {e}")
        
        # Check EasyOCR
        try:
            # Test EasyOCR initialization
            self._easyocr_reader = easyocr.Reader(['en'], gpu=self.default_config['easyocr_gpu'])
            self._easyocr_available = True
            self.logger.info("EasyOCR is available")
        except Exception as e:
            self._easyocr_available = False
            self.logger.warning(f"EasyOCR not available: {e}")
    
    
    def extract_text(self, image: Union[np.ndarray, Image.Image], 
                    engine: str = 'both', languages: List[str] = None) -> Dict[str, Any]:
        """
        Extract text dari image menggunakan specified engine(s)
        
        Args:
            image: Input image (numpy array atau PIL Image)
            engine: OCR engine to use ('tesseract', 'easyocr', 'both')
            languages: List of language codes untuk recognition
        
        Returns:
            dict: OCR result dengan text, confidence, dan metadata
        """
        start_time = time.time()
        
        try:
            # Convert image ke format yang sesuai
            image_array = self._prepare_image(image)
            
            if languages is None:
                languages = ['en', 'id']  # Default languages
            
            results = {}
            
            # Execute OCR berdasarkan engine selection
            if engine == 'tesseract' and self._tesseract_available:
                results['tesseract'] = self._extract_with_tesseract(image_array, languages)
            
            elif engine == 'easyocr' and self._easyocr_available:
                results['easyocr'] = self._extract_with_easyocr(image_array, languages)
            
            elif engine == 'both':
                # Run both engines jika tersedia
                if self._tesseract_available and self._easyocr_available:
                    # Parallel execution untuk performance
                    with ThreadPoolExecutor(max_workers=self.default_config['max_workers']) as executor:
                        future_tesseract = executor.submit(self._extract_with_tesseract, image_array, languages)
                        future_easyocr = executor.submit(self._extract_with_easyocr, image_array, languages)
                        
                        results['tesseract'] = future_tesseract.result()
                        results['easyocr'] = future_easyocr.result()
                
                elif self._tesseract_available:
                    results['tesseract'] = self._extract_with_tesseract(image_array, languages)
                
                elif self._easyocr_available:
                    results['easyocr'] = self._extract_with_easyocr(image_array, languages)
            
            if not results:
                return {
                    'text': '',
                    'confidence': 0,
                    'engine_used': 'none',
                    'processing_time': time.time() - start_time,
                    'error': 'No OCR engines available'
                }
            
            # Select best result
            best_result = self._select_best_result(results)
            best_result['processing_time'] = time.time() - start_time
            best_result['all_results'] = results
            
            return best_result
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return {
                'text': '',
                'confidence': 0,
                'engine_used': 'error',
                'processing_time': time.time() - start_time,
                'error': str(e)
            }
    
    
    def _prepare_image(self, image: Union[np.ndarray, Image.Image]) -> np.ndarray:
        """
        Prepare image untuk OCR processing
        
        Args:
            image: Input image
        
        Returns:
            np.ndarray: Processed image array
        """
        if isinstance(image, Image.Image):
            # Convert PIL Image ke numpy array
            image_array = np.array(image)
            
            # Convert RGBA ke RGB jika perlu
            if len(image_array.shape) == 3 and image_array.shape[2] == 4:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
            
            # Convert RGB ke BGR untuk OpenCV
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        
        elif isinstance(image, np.ndarray):
            image_array = image.copy()
        
        else:
            raise ValueError("Unsupported image format")
        
        return image_array
    
    
    def _extract_with_tesseract(self, image: np.ndarray, languages: List[str]) -> Dict[str, Any]:
        """
        Extract text menggunakan Tesseract OCR
        
        Args:
            image: Image array
            languages: Language codes
        
        Returns:
            dict: Tesseract OCR result
        """
        try:
            # Prepare language string untuk Tesseract
            lang_string = '+'.join(languages)
            
            # Configure Tesseract
            config = self.default_config['tesseract_config']
            
            # Extract text
            text = pytesseract.image_to_string(image, lang=lang_string, config=config)
            
            # Get confidence data
            data = pytesseract.image_to_data(image, lang=lang_string, config=config, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            # Get word-level details
            words = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:
                    words.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'bbox': {
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i]
                        }
                    })
            
            return {
                'text': text.strip(),
                'confidence': avg_confidence,
                'engine': 'tesseract',
                'languages': languages,
                'word_count': len([w for w in words if w['text'].strip()]),
                'words': words
            }
            
        except Exception as e:
            self.logger.error(f"Tesseract extraction failed: {e}")
            return {
                'text': '',
                'confidence': 0,
                'engine': 'tesseract',
                'error': str(e)
            }
    
    
    def _extract_with_easyocr(self, image: np.ndarray, languages: List[str]) -> Dict[str, Any]:
        """
        Extract text menggunakan EasyOCR
        
        Args:
            image: Image array
            languages: Language codes
        
        Returns:
            dict: EasyOCR result
        """
        try:
            # Initialize reader jika belum ada atau language berbeda
            if self._easyocr_reader is None:
                self._easyocr_reader = easyocr.Reader(languages, gpu=self.default_config['easyocr_gpu'])
            
            # Check jika perlu reinitialize untuk different languages
            current_langs = getattr(self._easyocr_reader, 'lang_list', [])
            if set(languages) != set(current_langs):
                self._easyocr_reader = easyocr.Reader(languages, gpu=self.default_config['easyocr_gpu'])
            
            # Extract text
            results = self._easyocr_reader.readtext(image)
            
            # Process results
            text_parts = []
            words = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                if confidence > self.default_config['confidence_threshold']:
                    text_parts.append(text)
                    confidences.append(confidence * 100)  # Convert ke percentage
                    
                    # Convert bbox format
                    bbox_array = np.array(bbox)
                    x_min, y_min = bbox_array.min(axis=0)
                    x_max, y_max = bbox_array.max(axis=0)
                    
                    words.append({
                        'text': text,
                        'confidence': confidence * 100,
                        'bbox': {
                            'x': int(x_min),
                            'y': int(y_min),
                            'width': int(x_max - x_min),
                            'height': int(y_max - y_min)
                        }
                    })
            
            # Combine text
            full_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': full_text.strip(),
                'confidence': avg_confidence,
                'engine': 'easyocr',
                'languages': languages,
                'word_count': len(words),
                'words': words
            }
            
        except Exception as e:
            self.logger.error(f"EasyOCR extraction failed: {e}")
            return {
                'text': '',
                'confidence': 0,
                'engine': 'easyocr',
                'error': str(e)
            }
    
    
    def _select_best_result(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select best result dari multiple OCR engines
        
        Args:
            results: Results dari different engines
        
        Returns:
            dict: Best OCR result
        """
        try:
            if not results:
                return {'text': '', 'confidence': 0, 'engine_used': 'none'}
            
            # Jika hanya satu result
            if len(results) == 1:
                engine_name, result = next(iter(results.items()))
                result['engine_used'] = engine_name
                return result
            
            # Multiple results - select based on criteria
            best_result = None
            best_score = -1
            
            for engine_name, result in results.items():
                if 'error' in result:
                    continue
                
                # Scoring criteria
                confidence = result.get('confidence', 0)
                text_length = len(result.get('text', '').strip())
                word_count = result.get('word_count', 0)
                
                # Calculate composite score
                score = (
                    confidence * 0.6 +  # Confidence weight: 60%
                    min(text_length / 100, 50) * 0.3 +  # Text length weight: 30% (capped)
                    min(word_count, 20) * 0.1  # Word count weight: 10% (capped)
                )
                
                if score > best_score:
                    best_score = score
                    best_result = result.copy()
                    best_result['engine_used'] = engine_name
            
            if best_result is None:
                # Fallback ke first available result
                engine_name, result = next(iter(results.items()))
                result['engine_used'] = engine_name
                return result
            
            return best_result
            
        except Exception as e:
            self.logger.error(f"Best result selection failed: {e}")
            return {'text': '', 'confidence': 0, 'engine_used': 'error', 'error': str(e)}
    
    
    def get_supported_languages(self) -> Dict[str, List[str]]:
        """
        Get supported languages untuk each engine
        
        Returns:
            dict: Supported languages per engine
        """
        languages = {}
        
        # Tesseract languages
        if self._tesseract_available:
            try:
                langs = pytesseract.get_languages()
                languages['tesseract'] = langs
            except Exception:
                languages['tesseract'] = ['eng', 'ind']  # Default fallback
        
        # EasyOCR languages
        if self._easyocr_available:
            try:
                # EasyOCR supported languages
                languages['easyocr'] = [
                    'en', 'id', 'zh', 'ja', 'ko', 'th', 'vi', 'ar', 'hi', 'ru',
                    'fr', 'de', 'es', 'pt', 'it', 'nl', 'pl', 'tr', 'sv', 'da',
                    'no', 'fi', 'cs', 'hu', 'ro', 'bg', 'hr', 'sr', 'sk', 'sl'
                ]
            except Exception:
                languages['easyocr'] = ['en', 'id']
        
        return languages
    
    
    def get_tesseract_info(self) -> Dict[str, Any]:
        """Get Tesseract engine information"""
        if not self._tesseract_available:
            return {'available': False, 'error': 'Tesseract not available'}
        
        try:
            version = pytesseract.get_tesseract_version()
            languages = pytesseract.get_languages()
            
            return {
                'available': True,
                'version': str(version),
                'languages': languages,
                'config': self.default_config['tesseract_config']
            }
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    
    def get_easyocr_info(self) -> Dict[str, Any]:
        """Get EasyOCR engine information"""
        if not self._easyocr_available:
            return {'available': False, 'error': 'EasyOCR not available'}
        
        try:
            import easyocr
            return {
                'available': True,
                'version': getattr(easyocr, '__version__', 'unknown'),
                'gpu_enabled': self.default_config['easyocr_gpu'],
                'languages': self.get_supported_languages().get('easyocr', [])
            }
        except Exception as e:
            return {'available': False, 'error': str(e)}
    
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get status dari semua OCR engines"""
        return {
            'tesseract': {
                'available': self._tesseract_available,
                'info': self.get_tesseract_info() if self._tesseract_available else None
            },
            'easyocr': {
                'available': self._easyocr_available,
                'info': self.get_easyocr_info() if self._easyocr_available else None
            },
            'recommended_engine': self._get_recommended_engine()
        }
    
    
    def _get_recommended_engine(self) -> str:
        """Get recommended engine berdasarkan availability"""
        if self._tesseract_available and self._easyocr_available:
            return 'both'
        elif self._tesseract_available:
            return 'tesseract'
        elif self._easyocr_available:
            return 'easyocr'
        else:
            return 'none'
