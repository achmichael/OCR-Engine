"""
Command Line Interface untuk OCR ML Engine - Updated Architecture
=================================================================

Module ini menyediakan CLI interface untuk menggunakan OCR Engine
dari command line dengan berbagai options dan parameters.

Author: AI Assistant
Date: August 2025
"""

import argparse
import os
import sys
import logging
import json
import glob
from pathlib import Path
from typing import List, Dict, Any

# Add project root ke Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import from new architecture
from app.services.ocr_service import OCRService
from app.services.pdf_service import PDFService
from app.services.image_service import ImageService
from app.utils.file_manager import FileManager
from app.utils.response_formatter import ResponseFormatter


class OCRCLI:
    """
    Updated Command Line Interface class untuk OCR Engine
    """
    
    def __init__(self):
        """Initialize CLI dengan services"""
        self.setup_logging()
        self.ocr_service = OCRService()
        self.pdf_service = PDFService()
        self.image_service = ImageService()
        self.file_manager = FileManager()
        self.response_formatter = ResponseFormatter()
        
        # CLI configuration
        self.supported_image_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp'}
        self.supported_pdf_formats = {'.pdf'}
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def process_single_image(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """
        Process single image file
        
        Args:
            image_path (str): Path ke image file
            **kwargs: Processing parameters
        
        Returns:
            dict: OCR result
        """
        try:
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'error': f'File not found: {image_path}'
                }
            
            # Load image
            image = self.image_service.load_image(image_path)
            if image is None:
                return {
                    'success': False,
                    'error': f'Could not load image: {image_path}'
                }
            
            # Apply enhancement
            enhancement_level = kwargs.get('enhancement_level', 2)
            enhanced_image = self.image_service.enhance_image(image, enhancement_level)
            
            # Perform OCR
            ocr_result = self.ocr_service.extract_text(
                enhanced_image,
                engine=kwargs.get('engine', 'both'),
                languages=kwargs.get('languages', ['en', 'id'])
            )
            
            return {
                'success': True,
                'filename': os.path.basename(image_path),
                'text': ocr_result.get('text', ''),
                'confidence': ocr_result.get('confidence', 0),
                'engine_used': ocr_result.get('engine_used', 'unknown'),
                'processing_time': ocr_result.get('processing_time', 0),
                'word_count': len(ocr_result.get('text', '').split()) if ocr_result.get('text') else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error processing image {image_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_pdf(self, pdf_path: str, **kwargs) -> Dict[str, Any]:
        """
        Process PDF file
        
        Args:
            pdf_path (str): Path ke PDF file
            **kwargs: Processing parameters
        
        Returns:
            dict: PDF processing result
        """
        try:
            if not os.path.exists(pdf_path):
                return {
                    'success': False,
                    'error': f'File not found: {pdf_path}'
                }
            
            # Extract text dari PDF
            result = self.pdf_service.extract_text_from_pdf(
                pdf_path,
                page_start=kwargs.get('page_start'),
                page_end=kwargs.get('page_end'),
                enhancement_level=kwargs.get('enhancement_level', 2),
                try_direct=kwargs.get('try_direct', True)
            )
            
            if 'error' in result:
                return {
                    'success': False,
                    'error': result['error']
                }
            
            # Combine text dari semua pages
            all_text = ' '.join([page.get('text', '') for page in result.get('pages', [])])
            
            return {
                'success': True,
                'filename': os.path.basename(pdf_path),
                'method': result.get('method', 'unknown'),
                'pages_processed': len(result.get('pages', [])),
                'text': all_text,
                'word_count': len(all_text.split()) if all_text else 0,
                'confidence': result.get('average_confidence', 0),
                'processing_time': result.get('total_time', 0),
                'pages': result.get('pages', [])
            }
            
        except Exception as e:
            self.logger.error(f"Error processing PDF {pdf_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_batch(self, file_paths: List[str], **kwargs) -> Dict[str, Any]:
        """
        Process multiple files
        
        Args:
            file_paths (list): List of file paths
            **kwargs: Processing parameters
        
        Returns:
            dict: Batch processing result
        """
        results = []
        successful = 0
        failed = 0
        
        for file_path in file_paths:
            self.logger.info(f"Processing: {file_path}")
            
            # Determine file type
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in self.supported_image_formats:
                result = self.process_single_image(file_path, **kwargs)
            elif file_ext in self.supported_pdf_formats:
                result = self.process_pdf(file_path, **kwargs)
            else:
                result = {
                    'success': False,
                    'filename': os.path.basename(file_path),
                    'error': f'Unsupported file format: {file_ext}'
                }
            
            results.append(result)
            
            if result.get('success', False):
                successful += 1
            else:
                failed += 1
        
        return {
            'total_files': len(file_paths),
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / len(file_paths)) * 100 if file_paths else 0,
            'results': results
        }
    
    def create_argument_parser(self) -> argparse.ArgumentParser:
        """Create command line argument parser"""
        parser = argparse.ArgumentParser(
            description='OCR ML Engine - Command Line Interface',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Process single image
  python ocr_cli.py -i image.jpg
  
  # Process PDF with page range
  python ocr_cli.py -p document.pdf --page-start 1 --page-end 5
  
  # Batch process multiple files
  python ocr_cli.py -b *.jpg *.png
  
  # Use specific OCR engine
  python ocr_cli.py -i image.jpg --engine tesseract
  
  # High enhancement level
  python ocr_cli.py -i image.jpg --enhancement 3
  
  # Output to JSON file
  python ocr_cli.py -i image.jpg --output result.json
            """
        )
        
        # Input options
        input_group = parser.add_mutually_exclusive_group(required=True)
        input_group.add_argument('-i', '--image', 
                               help='Process single image file')
        input_group.add_argument('-p', '--pdf', 
                               help='Process PDF file')
        input_group.add_argument('-b', '--batch', nargs='+',
                               help='Process multiple files (supports wildcards)')
        
        # Processing options
        parser.add_argument('--engine', choices=['tesseract', 'easyocr', 'both'],
                          default='both', help='OCR engine to use (default: both)')
        parser.add_argument('--enhancement', type=int, choices=[1, 2, 3],
                          default=2, help='Image enhancement level (default: 2)')
        parser.add_argument('--languages', nargs='+', default=['en', 'id'],
                          help='Language codes for OCR (default: en id)')
        
        # PDF specific options
        parser.add_argument('--page-start', type=int,
                          help='Starting page number for PDF processing')
        parser.add_argument('--page-end', type=int,
                          help='Ending page number for PDF processing')
        parser.add_argument('--no-direct', action='store_true',
                          help='Skip direct text extraction for PDF')
        
        # Output options
        parser.add_argument('-o', '--output',
                          help='Output file path (JSON format)')
        parser.add_argument('--text-only', action='store_true',
                          help='Output only extracted text')
        parser.add_argument('--verbose', '-v', action='store_true',
                          help='Verbose output')
        parser.add_argument('--quiet', '-q', action='store_true',
                          help='Quiet mode (minimal output)')
        
        return parser
    
    def expand_file_patterns(self, patterns: List[str]) -> List[str]:
        """
        Expand file patterns (wildcards) to actual file paths
        
        Args:
            patterns (list): List of file patterns
        
        Returns:
            list: Expanded file paths
        """
        expanded_files = []
        
        for pattern in patterns:
            if '*' in pattern or '?' in pattern:
                # Expand wildcard
                matches = glob.glob(pattern)
                expanded_files.extend(matches)
            else:
                # Regular file path
                expanded_files.append(pattern)
        
        # Remove duplicates dan filter existing files
        unique_files = list(set(expanded_files))
        existing_files = [f for f in unique_files if os.path.exists(f)]
        
        return existing_files
    
    def output_result(self, result: Dict[str, Any], args) -> None:
        """
        Output result berdasarkan command line options
        
        Args:
            result (dict): Processing result
            args: Command line arguments
        """
        if args.quiet:
            return
        
        if args.text_only:
            # Output only extracted text
            if isinstance(result, dict):
                if 'text' in result:
                    print(result['text'])
                elif 'results' in result:
                    # Batch result
                    for item in result['results']:
                        if item.get('success') and 'text' in item:
                            print(f"=== {item.get('filename', 'Unknown')} ===")
                            print(item['text'])
                            print()
            return
        
        if args.output:
            # Save ke JSON file
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Result saved to: {args.output}")
            except Exception as e:
                print(f"Error saving output: {e}")
        else:
            # Print ke console
            if args.verbose:
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                # Summary output
                self.print_summary(result)
    
    def print_summary(self, result: Dict[str, Any]) -> None:
        """Print summary of processing result"""
        if isinstance(result, dict):
            if 'results' in result:
                # Batch result
                print(f"Batch Processing Summary:")
                print(f"Total files: {result.get('total_files', 0)}")
                print(f"Successful: {result.get('successful', 0)}")
                print(f"Failed: {result.get('failed', 0)}")
                print(f"Success rate: {result.get('success_rate', 0):.1f}%")
                print()
                
                # Show individual results
                for item in result.get('results', []):
                    status = "✓" if item.get('success') else "✗"
                    filename = item.get('filename', 'Unknown')
                    if item.get('success'):
                        word_count = item.get('word_count', 0)
                        confidence = item.get('confidence', 0)
                        print(f"{status} {filename} - {word_count} words, {confidence:.1f}% confidence")
                    else:
                        error = item.get('error', 'Unknown error')
                        print(f"{status} {filename} - Error: {error}")
            
            elif result.get('success'):
                # Single file result
                filename = result.get('filename', 'Unknown')
                word_count = result.get('word_count', 0)
                confidence = result.get('confidence', 0)
                processing_time = result.get('processing_time', 0)
                
                print(f"✓ {filename}")
                print(f"Words extracted: {word_count}")
                print(f"Confidence: {confidence:.1f}%")
                print(f"Processing time: {processing_time:.2f}s")
                
                if 'engine_used' in result:
                    print(f"Engine: {result['engine_used']}")
                
                if 'method' in result:
                    print(f"Method: {result['method']}")
                
                if 'pages_processed' in result:
                    print(f"Pages processed: {result['pages_processed']}")
            
            else:
                # Error result
                error = result.get('error', 'Unknown error')
                print(f"✗ Error: {error}")
    
    def run(self) -> int:
        """
        Main CLI run method
        
        Returns:
            int: Exit code (0 for success, 1 for error)
        """
        try:
            parser = self.create_argument_parser()
            args = parser.parse_args()
            
            # Setup logging level
            if args.verbose:
                logging.getLogger().setLevel(logging.DEBUG)
            elif args.quiet:
                logging.getLogger().setLevel(logging.ERROR)
            
            # Prepare processing parameters
            kwargs = {
                'engine': args.engine,
                'enhancement_level': args.enhancement,
                'languages': args.languages,
                'try_direct': not args.no_direct
            }
            
            if args.page_start:
                kwargs['page_start'] = args.page_start
            if args.page_end:
                kwargs['page_end'] = args.page_end
            
            # Process based on input type
            if args.image:
                self.logger.info(f"Processing image: {args.image}")
                result = self.process_single_image(args.image, **kwargs)
            
            elif args.pdf:
                self.logger.info(f"Processing PDF: {args.pdf}")
                result = self.process_pdf(args.pdf, **kwargs)
            
            elif args.batch:
                file_paths = self.expand_file_patterns(args.batch)
                if not file_paths:
                    print("No files found matching the specified patterns")
                    return 1
                
                self.logger.info(f"Processing {len(file_paths)} files")
                result = self.process_batch(file_paths, **kwargs)
            
            # Output result
            self.output_result(result, args)
            
            # Return appropriate exit code
            if isinstance(result, dict):
                if 'results' in result:
                    # Batch result
                    return 0 if result.get('successful', 0) > 0 else 1
                else:
                    # Single file result
                    return 0 if result.get('success', False) else 1
            
            return 0
            
        except KeyboardInterrupt:
            self.logger.info("Process interrupted by user")
            return 1
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return 1


def main():
    """Main entry point"""
    cli = OCRCLI()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
