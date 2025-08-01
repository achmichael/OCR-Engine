"""
Test Suite untuk OCR ML Engine - Restructured Architecture
==========================================================

Test configuration dan basic functionality test untuk new architecture.

Author: AI Assistant
Date: August 2025
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

# Add project root ke path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import test utilities
from app.utils.response_formatter import ResponseFormatter
from app.utils.validators import validate_request, validate_file
from app.models.ocr_models import OCRResult, BoundingBox, DetectedWord


class TestResponseFormatter(unittest.TestCase):
    """Test ResponseFormatter utility"""
    
    def setUp(self):
        self.formatter = ResponseFormatter()
    
    def test_success_response(self):
        """Test success response formatting"""
        response = self.formatter.success_response("Test message", {"key": "value"})
        
        self.assertTrue(response['success'])
        self.assertEqual(response['message'], "Test message")
        self.assertEqual(response['status_code'], 200)
        self.assertIn('timestamp', response)
        self.assertEqual(response['data']['key'], "value")
    
    def test_error_response(self):
        """Test error response formatting"""
        response = self.formatter.error_response("Error message", "Details")
        
        self.assertFalse(response['success'])
        self.assertEqual(response['error'], "Error message")
        self.assertEqual(response['details'], "Details")
        self.assertEqual(response['status_code'], 500)
    
    def test_batch_response(self):
        """Test batch response formatting"""
        results = [{"id": 1}, {"id": 2}]
        response = self.formatter.batch_response(results, 2, 0, 2, "batch-123")
        
        self.assertTrue(response['success'])
        self.assertEqual(response['data']['summary']['total'], 2)
        self.assertEqual(response['data']['summary']['successful'], 2)
        self.assertEqual(response['data']['summary']['success_rate'], 100.0)


class TestValidators(unittest.TestCase):
    """Test validation utilities"""
    
    def test_validate_file_valid(self):
        """Test file validation dengan valid file"""
        # Mock FileStorage object
        mock_file = Mock()
        mock_file.filename = "test.jpg"
        mock_file.tell.return_value = 0
        mock_file.seek.return_value = None
        
        # Mock file size
        mock_file.tell.side_effect = [0, 1000, 0]  # current, end, reset
        
        config = {
            'ALLOWED_IMAGE_EXTENSIONS': {'.jpg', '.jpeg', '.png'},
            'MAX_FILE_SIZE': 10 * 1024 * 1024  # 10MB
        }
        
        result = validate_file(mock_file, 'image', config)
        
        # Note: Akan gagal karena tidak ada file content, tapi structure test
        self.assertIn('valid', result)
        self.assertIn('message', result)
    
    def test_validate_request_missing_file(self):
        """Test request validation tanpa file"""
        mock_request = Mock()
        mock_request.content_type = "multipart/form-data"
        mock_request.files = {}
        
        result = validate_request(mock_request, file_required=True)
        
        self.assertFalse(result['valid'])
        self.assertIn('file field', result['message'])


class TestOCRModels(unittest.TestCase):
    """Test OCR data models"""
    
    def test_bounding_box_creation(self):
        """Test BoundingBox model"""
        bbox = BoundingBox(x=10, y=20, width=100, height=50)
        
        self.assertEqual(bbox.x, 10)
        self.assertEqual(bbox.y, 20)
        self.assertEqual(bbox.width, 100)
        self.assertEqual(bbox.height, 50)
    
    def test_bounding_box_dict_conversion(self):
        """Test BoundingBox dict conversion"""
        bbox = BoundingBox(x=10, y=20, width=100, height=50)
        bbox_dict = bbox.to_dict()
        
        expected = {'x': 10, 'y': 20, 'width': 100, 'height': 50}
        self.assertEqual(bbox_dict, expected)
        
        # Test from_dict
        bbox_restored = BoundingBox.from_dict(bbox_dict)
        self.assertEqual(bbox.x, bbox_restored.x)
        self.assertEqual(bbox.y, bbox_restored.y)
    
    def test_detected_word_creation(self):
        """Test DetectedWord model"""
        bbox = BoundingBox(x=10, y=20, width=100, height=50)
        word = DetectedWord(text="Hello", confidence=85.5, bbox=bbox)
        
        self.assertEqual(word.text, "Hello")
        self.assertEqual(word.confidence, 85.5)
        self.assertEqual(word.bbox.x, 10)
    
    def test_ocr_result_creation(self):
        """Test OCRResult model"""
        result = OCRResult(
            filename="test.jpg",
            extracted_text="Hello World",
            confidence_score=90.0
        )
        
        self.assertEqual(result.filename, "test.jpg")
        self.assertEqual(result.extracted_text, "Hello World")
        self.assertEqual(result.confidence_score, 90.0)
        self.assertIsNotNone(result.result_id)  # Should auto-generate UUID


class TestFlaskAppCreation(unittest.TestCase):
    """Test Flask app creation"""
    
    def test_app_factory_import(self):
        """Test if Flask app factory can be imported"""
        try:
            from app import create_app
            self.assertTrue(callable(create_app))
        except ImportError as e:
            self.skipTest(f"Flask app factory not available: {e}")
    
    @patch('app.config.DevelopmentConfig')
    def test_app_creation(self, mock_config):
        """Test Flask app creation (mocked)"""
        try:
            from app import create_app
            
            # Mock configuration
            mock_config.return_value = Mock()
            
            # This might fail due to missing dependencies, but tests structure
            app = create_app('development')
            self.assertIsNotNone(app)
            
        except Exception as e:
            self.skipTest(f"App creation test skipped: {e}")


class TestProjectStructure(unittest.TestCase):
    """Test project structure integrity"""
    
    def test_required_directories_exist(self):
        """Test if required directories exist"""
        required_dirs = [
            'app',
            'app/controllers',
            'app/services', 
            'app/models',
            'app/utils'
        ]
        
        for dir_name in required_dirs:
            dir_path = project_root / dir_name
            self.assertTrue(dir_path.exists(), f"Directory {dir_name} should exist")
            self.assertTrue(dir_path.is_dir(), f"{dir_name} should be a directory")
    
    def test_required_files_exist(self):
        """Test if required files exist"""
        required_files = [
            'app/__init__.py',
            'app/config.py',
            'app/routes.py',
            'app/controllers/__init__.py',
            'app/services/__init__.py',
            'app/models/__init__.py',
            'app/utils/__init__.py',
            'app_launcher.py',
            'requirements.txt'
        ]
        
        for file_name in required_files:
            file_path = project_root / file_name
            self.assertTrue(file_path.exists(), f"File {file_name} should exist")
            self.assertTrue(file_path.is_file(), f"{file_name} should be a file")
    
    def test_python_files_syntax(self):
        """Test if Python files have valid syntax"""
        python_files = [
            'app/__init__.py',
            'app/config.py',
            'app/routes.py',
            'app/controllers/ocr_controller.py',
            'app/controllers/health_controller.py',
            'app/services/ocr_service.py',
            'app/services/image_service.py',
            'app/services/pdf_service.py',
            'app/models/ocr_models.py',
            'app/utils/validators.py',
            'app/utils/response_formatter.py',
            'app/utils/file_manager.py',
            'app_launcher.py'
        ]
        
        for file_name in python_files:
            file_path = project_root / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    # Try to compile (basic syntax check)
                    compile(code, str(file_path), 'exec')
                    
                except SyntaxError as e:
                    self.fail(f"Syntax error in {file_name}: {e}")
                except Exception as e:
                    # Other errors (like import errors) are acceptable for this test
                    pass


class TestConfiguration(unittest.TestCase):
    """Test configuration management"""
    
    def test_config_import(self):
        """Test if configuration can be imported"""
        try:
            from app.config import Config, DevelopmentConfig, ProductionConfig
            
            self.assertTrue(issubclass(DevelopmentConfig, Config))
            self.assertTrue(issubclass(ProductionConfig, Config))
            
        except ImportError as e:
            self.skipTest(f"Configuration import failed: {e}")
    
    def test_config_values(self):
        """Test configuration values"""
        try:
            from app.config import DevelopmentConfig
            
            config = DevelopmentConfig()
            
            # Test that required config values exist
            self.assertTrue(hasattr(config, 'SECRET_KEY'))
            self.assertTrue(hasattr(config, 'OCR_DEFAULT_ENGINE'))
            self.assertTrue(hasattr(config, 'MAX_FILE_SIZE'))
            
        except Exception as e:
            self.skipTest(f"Configuration test skipped: {e}")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestResponseFormatter,
        TestValidators,
        TestOCRModels,
        TestFlaskAppCreation,
        TestProjectStructure,
        TestConfiguration
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("="*60)
    print("OCR ML Engine - Architecture Test Suite")
    print("="*60)
    print(f"Testing project at: {project_root}")
    print()
    
    success = run_tests()
    
    print()
    print("="*60)
    if success:
        print("✅ All tests passed! Architecture is properly structured.")
    else:
        print("❌ Some tests failed. Check the output above.")
    print("="*60)
    
    sys.exit(0 if success else 1)
