"""
OCR Result Models
=================

Data models untuk OCR results dan related entities.

Author: AI Assistant
Date: August 2025
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid


@dataclass
class BoundingBox:
    """Bounding box untuk detected text"""
    x: int
    y: int
    width: int
    height: int
    
    def to_dict(self) -> Dict[str, int]:
        """Convert ke dictionary"""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'BoundingBox':
        """Create dari dictionary"""
        return cls(
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height']
        )


@dataclass
class DetectedWord:
    """Individual detected word dengan metadata"""
    text: str
    confidence: float
    bbox: BoundingBox
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ke dictionary"""
        return {
            'text': self.text,
            'confidence': self.confidence,
            'bbox': self.bbox.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DetectedWord':
        """Create dari dictionary"""
        return cls(
            text=data['text'],
            confidence=data['confidence'],
            bbox=BoundingBox.from_dict(data['bbox'])
        )


@dataclass
class ImageStats:
    """Image statistics dan quality metrics"""
    width: int
    height: int
    total_pixels: int
    mode: str
    channels: int
    mean_brightness: float
    std_brightness: float
    contrast: float
    min_value: float
    max_value: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ke dictionary"""
        return {
            'dimensions': {
                'width': self.width,
                'height': self.height,
                'total_pixels': self.total_pixels
            },
            'color_info': {
                'mode': self.mode,
                'channels': self.channels
            },
            'quality_metrics': {
                'mean_brightness': self.mean_brightness,
                'std_brightness': self.std_brightness,
                'contrast': self.contrast,
                'min_value': self.min_value,
                'max_value': self.max_value
            }
        }


@dataclass
class TextStatistics:
    """Text content statistics"""
    character_count: int
    word_count: int
    line_count: int
    paragraph_count: int
    has_numbers: bool
    has_special_chars: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ke dictionary"""
        return {
            'character_count': self.character_count,
            'word_count': self.word_count,
            'line_count': self.line_count,
            'paragraph_count': self.paragraph_count,
            'has_numbers': self.has_numbers,
            'has_special_chars': self.has_special_chars
        }


@dataclass
class OCRResult:
    """Complete OCR result untuk single image"""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    file_size: int = 0
    processing_time: float = 0.0
    enhancement_level: int = 2
    engine_used: str = ""
    languages: List[str] = field(default_factory=list)
    extracted_text: str = ""
    confidence_score: float = 0.0
    statistics: Optional[TextStatistics] = None
    detected_words: List[DetectedWord] = field(default_factory=list)
    image_stats: Optional[ImageStats] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ke dictionary untuk JSON serialization"""
        return {
            'result_id': self.result_id,
            'filename': self.filename,
            'file_size': self.file_size,
            'processing_time': self.processing_time,
            'enhancement_level': self.enhancement_level,
            'engine_used': self.engine_used,
            'languages': self.languages,
            'extracted_text': self.extracted_text,
            'confidence_score': self.confidence_score,
            'statistics': self.statistics.to_dict() if self.statistics else None,
            'detected_words': [word.to_dict() for word in self.detected_words],
            'image_stats': self.image_stats.to_dict() if self.image_stats else None,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class PDFPageResult:
    """OCR result untuk single PDF page"""
    page_number: int
    text: str = ""
    extraction_method: str = ""  # 'direct' atau 'ocr'
    confidence: float = 0.0
    word_count: int = 0
    engine_used: str = ""
    processing_time: float = 0.0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ke dictionary"""
        return {
            'page_number': self.page_number,
            'text': self.text,
            'extraction_method': self.extraction_method,
            'confidence': self.confidence,
            'word_count': self.word_count,
            'engine_used': self.engine_used,
            'processing_time': self.processing_time,
            'error': self.error
        }


@dataclass
class PDFInfo:
    """PDF file information"""
    filename: str
    file_size: int
    page_count: int
    has_extractable_text: bool
    sample_text_length: int
    metadata: Dict[str, str] = field(default_factory=dict)
    processing_recommendation: str = "ocr"  # 'direct' atau 'ocr'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ke dictionary"""
        return {
            'filename': self.filename,
            'file_size': self.file_size,
            'page_count': self.page_count,
            'has_extractable_text': self.has_extractable_text,
            'sample_text_length': self.sample_text_length,
            'metadata': self.metadata,
            'processing_recommendation': self.processing_recommendation
        }


@dataclass
class PDFResult:
    """Complete PDF processing result"""
    result_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    filename: str = ""
    file_size: int = 0
    pdf_info: Optional[PDFInfo] = None
    processing_method: str = ""  # 'direct' atau 'ocr'
    pages_processed: int = 0
    total_processing_time: float = 0.0
    enhancement_level: int = 2
    pages: List[PDFPageResult] = field(default_factory=list)
    full_text: str = ""
    average_confidence: float = 0.0
    statistics: Optional[TextStatistics] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ke dictionary"""
        return {
            'result_id': self.result_id,
            'filename': self.filename,
            'file_size': self.file_size,
            'pdf_info': self.pdf_info.to_dict() if self.pdf_info else None,
            'processing_method': self.processing_method,
            'pages_processed': self.pages_processed,
            'total_processing_time': self.total_processing_time,
            'enhancement_level': self.enhancement_level,
            'pages': [page.to_dict() for page in self.pages],
            'full_text': self.full_text,
            'average_confidence': self.average_confidence,
            'statistics': self.statistics.to_dict() if self.statistics else None,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class BatchResult:
    """Batch processing result"""
    batch_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    success_rate: float = 0.0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    results: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ke dictionary"""
        return {
            'batch_id': self.batch_id,
            'total_files': self.total_files,
            'successful': self.successful,
            'failed': self.failed,
            'success_rate': self.success_rate,
            'total_processing_time': self.total_processing_time,
            'average_processing_time': self.average_processing_time,
            'results': self.results,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class EngineInfo:
    """OCR Engine information"""
    name: str
    available: bool
    version: str = ""
    languages: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ke dictionary"""
        return {
            'name': self.name,
            'available': self.available,
            'version': self.version,
            'languages': self.languages,
            'config': self.config,
            'error': self.error
        }


@dataclass
class SystemHealth:
    """System health information"""
    status: str = "unknown"  # 'healthy', 'warning', 'critical'
    uptime: str = ""
    response_time: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    dependencies: Dict[str, bool] = field(default_factory=dict)
    engines: Dict[str, EngineInfo] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ke dictionary"""
        return {
            'status': self.status,
            'uptime': self.uptime,
            'response_time': self.response_time,
            'system_metrics': {
                'cpu_usage': self.cpu_usage,
                'memory_usage': self.memory_usage,
                'disk_usage': self.disk_usage
            },
            'dependencies': self.dependencies,
            'engines': {name: engine.to_dict() for name, engine in self.engines.items()},
            'timestamp': self.timestamp.isoformat()
        }
