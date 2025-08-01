"""
Image Service
=============

Service untuk image processing dan enhancement operations.

Author: AI Assistant
Date: August 2025
"""

import logging
from typing import Optional, Tuple, Union
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2


class ImageService:
    """
    Service untuk image processing operations
    
    Features:
    - Image loading dan validation
    - Multi-level enhancement
    - Preprocessing untuk OCR
    - Format conversion
    """
    
    def __init__(self):
        """Initialize Image Service"""
        self.logger = logging.getLogger(__name__)
        
        # Enhancement configurations
        self.enhancement_configs = {
            1: {  # Light enhancement
                'denoise_strength': 3,
                'sharpen_factor': 1.1,
                'contrast_factor': 1.1,
                'brightness_factor': 1.0
            },
            2: {  # Medium enhancement  
                'denoise_strength': 5,
                'sharpen_factor': 1.2,
                'contrast_factor': 1.3,
                'brightness_factor': 1.1
            },
            3: {  # Heavy enhancement
                'denoise_strength': 7,
                'sharpen_factor': 1.4,
                'contrast_factor': 1.5,
                'brightness_factor': 1.2
            }
        }
    
    
    def load_image(self, image_path: str) -> Optional[Image.Image]:
        """
        Load image dari file path
        
        Args:
            image_path (str): Path ke image file
        
        Returns:
            PIL.Image: Loaded image atau None jika gagal
        """
        try:
            # Load image dengan PIL
            image = Image.open(image_path)
            
            # Convert ke RGB jika bukan RGB mode
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            self.logger.info(f"Successfully loaded image: {image_path} ({image.size})")
            return image
            
        except Exception as e:
            self.logger.error(f"Failed to load image {image_path}: {e}")
            return None
    
    
    def enhance_image(self, image: Image.Image, level: int = 2) -> Image.Image:
        """
        Apply enhancement ke image untuk improve OCR accuracy
        
        Args:
            image (PIL.Image): Input image
            level (int): Enhancement level (1=light, 2=medium, 3=heavy)
        
        Returns:
            PIL.Image: Enhanced image
        """
        try:
            if level not in self.enhancement_configs:
                level = 2  # Default ke medium
            
            config = self.enhancement_configs[level]
            enhanced_image = image.copy()
            
            cv_image = np.array(enhanced_image)
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
            
            cv_image = cv2.fastNlMeansDenoisingColored(
                cv_image, None, config['denoise_strength'], config['denoise_strength'], 7, 21
            )
            
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            enhanced_image = Image.fromarray(cv_image)
            
            contrast_enhancer = ImageEnhance.Contrast(enhanced_image)
            enhanced_image = contrast_enhancer.enhance(config['contrast_factor'])
            
            brightness_enhancer = ImageEnhance.Brightness(enhanced_image)
            enhanced_image = brightness_enhancer.enhance(config['brightness_factor'])
            
            # 5. Sharpening
            sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
            enhanced_image = sharpness_enhancer.enhance(config['sharpen_factor'])
            
            # 6. Additional processing untuk text clarity
            enhanced_image = self._apply_text_enhancement(enhanced_image, level)
            
            self.logger.info(f"Applied enhancement level {level} to image")
            return enhanced_image
            
        except Exception as e:
            self.logger.error(f"Image enhancement failed: {e}")
            return image  # Return original jika enhancement gagal
    
    
    def _apply_text_enhancement(self, image: Image.Image, level: int) -> Image.Image:
        """
        Apply specific enhancements untuk text recognition
        
        Args:
            image (PIL.Image): Input image
            level (int): Enhancement level
        
        Returns:
            PIL.Image: Text-enhanced image
        """
        try:
            # Convert ke grayscale untuk text processing
            gray_image = image.convert('L')
            
            # Convert ke OpenCV format
            cv_gray = np.array(gray_image)
            
            # Apply adaptive thresholding untuk better text separation
            if level >= 2:
                # Gaussian adaptive threshold
                binary = cv2.adaptiveThreshold(
                    cv_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                )
                
                # Morphological operations untuk clean up
                if level == 3:
                    kernel = np.ones((2, 2), np.uint8)
                    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
                    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
                
                # Convert back ke RGB
                enhanced = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
                return Image.fromarray(enhanced)
            
            else:
                # Light enhancement - just return original
                return image
                
        except Exception as e:
            self.logger.error(f"Text enhancement failed: {e}")
            return image
    
    
    def resize_image(self, image: Image.Image, max_width: int = 2000, max_height: int = 2000) -> Image.Image:
        """
        Resize image untuk optimal OCR processing
        
        Args:
            image (PIL.Image): Input image
            max_width (int): Maximum width
            max_height (int): Maximum height
        
        Returns:
            PIL.Image: Resized image
        """
        try:
            width, height = image.size
            
            # Calculate scale factor
            scale_w = max_width / width if width > max_width else 1
            scale_h = max_height / height if height > max_height else 1
            scale = min(scale_w, scale_h)
            
            if scale < 1:
                new_width = int(width * scale)
                new_height = int(height * scale)
                
                # Use high-quality resampling
                resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.logger.info(f"Resized image from {width}x{height} to {new_width}x{new_height}")
                return resized_image
            
            return image
            
        except Exception as e:
            self.logger.error(f"Image resize failed: {e}")
            return image
    
    
    def rotate_image(self, image: Image.Image, angle: float) -> Image.Image:
        """
        Rotate image berdasarkan angle
        
        Args:
            image (PIL.Image): Input image
            angle (float): Rotation angle dalam degrees
        
        Returns:
            PIL.Image: Rotated image
        """
        try:
            if angle != 0:
                rotated = image.rotate(angle, expand=True, fillcolor='white')
                self.logger.info(f"Rotated image by {angle} degrees")
                return rotated
            return image
            
        except Exception as e:
            self.logger.error(f"Image rotation failed: {e}")
            return image
    
    
    def detect_orientation(self, image: Image.Image) -> float:
        """
        Detect text orientation dalam image
        
        Args:
            image (PIL.Image): Input image
        
        Returns:
            float: Detected rotation angle
        """
        try:
            # Convert ke OpenCV format
            cv_image = np.array(image)
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Find contours
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                angles = []
                for rho, theta in lines[:, 0]:
                    angle = (theta - np.pi/2) * 180 / np.pi
                    angles.append(angle)
                
                # Find most common angle
                if angles:
                    angle = np.median(angles)
                    # Normalize ke [-45, 45] range
                    if angle > 45:
                        angle -= 90
                    elif angle < -45:
                        angle += 90
                    
                    return angle
            
            return 0  # No rotation detected
            
        except Exception as e:
            self.logger.error(f"Orientation detection failed: {e}")
            return 0
    
    
    def auto_correct_orientation(self, image: Image.Image) -> Image.Image:
        """
        Automatically correct image orientation
        
        Args:
            image (PIL.Image): Input image
        
        Returns:
            PIL.Image: Orientation-corrected image
        """
        try:
            detected_angle = self.detect_orientation(image)
            
            # Only apply correction jika angle significant
            if abs(detected_angle) > 1:  # 1 degree threshold
                corrected = self.rotate_image(image, -detected_angle)
                self.logger.info(f"Auto-corrected orientation by {-detected_angle} degrees")
                return corrected
            
            return image
            
        except Exception as e:
            self.logger.error(f"Auto orientation correction failed: {e}")
            return image
    
    
    def crop_text_region(self, image: Image.Image, padding: int = 10) -> Image.Image:
        """
        Crop image ke text region untuk better OCR
        
        Args:
            image (PIL.Image): Input image
            padding (int): Padding around detected text region
        
        Returns:
            PIL.Image: Cropped image
        """
        try:
            # Convert ke OpenCV format
            cv_image = np.array(image)
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # Find text regions
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Get bounding rectangle dari all contours
                x_min, y_min = float('inf'), float('inf')
                x_max, y_max = 0, 0
                
                for contour in contours:
                    x, y, w, h = cv2.boundingRect(contour)
                    x_min = min(x_min, x)
                    y_min = min(y_min, y)
                    x_max = max(x_max, x + w)
                    y_max = max(y_max, y + h)
                
                # Add padding
                height, width = gray.shape
                x_min = max(0, x_min - padding)
                y_min = max(0, y_min - padding)
                x_max = min(width, x_max + padding)
                y_max = min(height, y_max + padding)
                
                # Crop image
                cropped = image.crop((x_min, y_min, x_max, y_max))
                self.logger.info(f"Cropped text region: ({x_min}, {y_min}, {x_max}, {y_max})")
                return cropped
            
            return image
            
        except Exception as e:
            self.logger.error(f"Text region cropping failed: {e}")
            return image
    
    
    def get_image_stats(self, image: Image.Image) -> dict:
        """
        Get statistical information tentang image
        
        Args:
            image (PIL.Image): Input image
        
        Returns:
            dict: Image statistics
        """
        try:
            width, height = image.size
            mode = image.mode
            
            # Convert ke array untuk stats
            img_array = np.array(image)
            
            stats = {
                'dimensions': {
                    'width': width,
                    'height': height,
                    'total_pixels': width * height
                },
                'color_info': {
                    'mode': mode,
                    'channels': len(img_array.shape) if len(img_array.shape) > 2 else 1
                },
                'quality_metrics': {
                    'mean_brightness': float(np.mean(img_array)),
                    'std_brightness': float(np.std(img_array)),
                    'min_value': float(np.min(img_array)),
                    'max_value': float(np.max(img_array))
                }
            }
            
            # Calculate contrast ratio
            if len(img_array.shape) == 3:
                # Color image - convert ke grayscale untuk contrast calculation
                gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
                contrast = np.std(gray)
            else:
                contrast = np.std(img_array)
            
            stats['quality_metrics']['contrast'] = float(contrast)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get image stats: {e}")
            return {
                'error': str(e),
                'dimensions': {'width': 0, 'height': 0},
                'color_info': {'mode': 'unknown'},
                'quality_metrics': {}
            }
