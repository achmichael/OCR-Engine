#!/usr/bin/env python3
"""
OCR ML Engine Application Launcher
==================================

Main launcher untuk OCR ML Engine dengan restructured architecture.
Mendukung multiple interfaces: CLI, GUI, dan Web API.

Author: AI Assistant
Date: August 2025
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# Add project root ke Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def setup_environment():
    """Setup environment variables dan configuration"""
    # Set default environment
    os.environ.setdefault('FLASK_ENV', 'development')
    os.environ.setdefault('FLASK_DEBUG', '1')
    
    # Create necessary directories
    directories = [
        'temp',
        'results',
        'logs',
        'uploads'
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(exist_ok=True)
        logger.info(f"Ensured directory exists: {dir_path}")


def launch_web_api(host='127.0.0.1', port=5000, debug=True):
    """
    Launch Web API server
    
    Args:
        host (str): Host address
        port (int): Port number
        debug (bool): Debug mode
    """
    try:
        from app import create_app
        
        logger.info("Starting OCR ML Engine Web API...")
        logger.info(f"Server will run on: http://{host}:{port}")
        
        # Create Flask application
        app = create_app()
        
        # Run development server
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except ImportError as e:
        logger.error(f"Failed to import Flask app: {e}")
        logger.error("Please install required dependencies: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start web API: {e}")
        sys.exit(1)


def launch_cli():
    """Launch Command Line Interface"""
    try:
        # Import dari existing CLI module (akan di-update nanti)
        from ocr_cli import main as cli_main
        logger.info("Starting OCR ML Engine CLI...")
        cli_main()
        
    except ImportError:
        logger.error("CLI module not found. Please ensure ocr_cli.py exists.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start CLI: {e}")
        sys.exit(1)


def launch_gui():
    """Launch Graphical User Interface"""
    try:
        # Import dari existing GUI module (akan di-update nanti)
        from ocr_gui import main as gui_main
        logger.info("Starting OCR ML Engine GUI...")
        gui_main()
        
    except ImportError:
        logger.error("GUI module not found. Please ensure ocr_gui.py exists.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start GUI: {e}")
        sys.exit(1)


def run_tests():
    """Run test suite"""
    try:
        import pytest
        logger.info("Running OCR ML Engine tests...")
        
        # Run pytest dengan coverage
        test_args = [
            'tests/',
            '-v',
            '--tb=short',
            '--cov=app',
            '--cov-report=term-missing'
        ]
        
        exit_code = pytest.main(test_args)
        sys.exit(exit_code)
        
    except ImportError:
        logger.error("pytest not available. Install with: pip install pytest pytest-cov")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to run tests: {e}")
        sys.exit(1)


def install_dependencies():
    """Install required dependencies"""
    try:
        import subprocess
        
        logger.info("Installing dependencies...")
        
        # Install dari requirements.txt
        requirements_file = project_root / 'requirements.txt'
        if requirements_file.exists():
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ])
            logger.info("Dependencies installed successfully!")
        else:
            logger.error("requirements.txt not found!")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        sys.exit(1)


def check_dependencies():
    """Check if required dependencies are installed"""
    # Mapping package name ke import name
    package_import_map = {
        'flask': 'flask',
        'opencv-python': 'cv2',
        'Pillow': 'PIL',
        'numpy': 'numpy',
        'pytesseract': 'pytesseract',
        'easyocr': 'easyocr',
        'pdf2image': 'pdf2image',
        'PyPDF2': 'PyPDF2'
    }
    
    missing_packages = []
    
    for package, import_name in package_import_map.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"Missing packages: {', '.join(missing_packages)}")
        logger.info("Run 'python app_launcher.py --install' to install dependencies")
        return False
    
    logger.info("All required dependencies are available")
    return True


def show_system_info():
    """Show system information dan dependencies status"""
    import platform
    import pkg_resources
    
    print("\n" + "="*60)
    print("OCR ML Engine - System Information")
    print("="*60)
    
    # System info
    print(f"Python Version: {sys.version}")
    print(f"Platform: {platform.platform()}")
    print(f"Architecture: {platform.architecture()[0]}")
    print(f"Project Root: {project_root}")
    
    # Dependencies status
    print("\nDependency Status:")
    print("-" * 30)
    
    required_packages = [
        'flask', 'opencv-python', 'Pillow', 'numpy', 
        'pytesseract', 'easyocr', 'pdf2image', 'PyPDF2'
    ]
    
    for package in required_packages:
        try:
            version = pkg_resources.get_distribution(package).version
            print(f"✓ {package}: {version}")
        except pkg_resources.DistributionNotFound:
            print(f"✗ {package}: Not installed")
    
    # Check OCR engines
    print("\nOCR Engines Status:")
    print("-" * 30)
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract OCR: {version}")
    except Exception:
        print("✗ Tesseract OCR: Not available")
    
    try:
        import easyocr
        print(f"✓ EasyOCR: Available")
    except Exception:
        print("✗ EasyOCR: Not available")
    
    print("="*60)


def main():
    """Main application launcher"""
    parser = argparse.ArgumentParser(
        description='OCR ML Engine - Multi-Interface Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app_launcher.py --web                 # Start web API server
  python app_launcher.py --cli                 # Start CLI interface
  python app_launcher.py --gui                 # Start GUI interface
  python app_launcher.py --test                # Run tests
  python app_launcher.py --install             # Install dependencies
  python app_launcher.py --info                # Show system info
        """
    )
    
    # Interface options
    interface_group = parser.add_mutually_exclusive_group()
    interface_group.add_argument('--web', action='store_true', 
                               help='Launch Web API server (default)')
    interface_group.add_argument('--cli', action='store_true', 
                               help='Launch Command Line Interface')
    interface_group.add_argument('--gui', action='store_true', 
                               help='Launch Graphical User Interface')
    
    # Utility options
    parser.add_argument('--test', action='store_true', 
                       help='Run test suite')
    parser.add_argument('--install', action='store_true', 
                       help='Install required dependencies')
    parser.add_argument('--info', action='store_true', 
                       help='Show system information')
    
    # Web server options
    parser.add_argument('--host', default='127.0.0.1', 
                       help='Host address for web server (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5000, 
                       help='Port for web server (default: 5000)')
    parser.add_argument('--no-debug', action='store_true', 
                       help='Disable debug mode')
    
    args = parser.parse_args()
    
    # Setup environment
    setup_environment()
    
    # Handle utility commands
    if args.install:
        install_dependencies()
        return
    
    if args.info:
        show_system_info()
        return
    
    if args.test:
        run_tests()
        return
    
    # Check dependencies untuk interface commands
    if not check_dependencies():
        logger.error("Please install missing dependencies first")
        return
    
    # Launch appropriate interface
    if args.cli:
        launch_cli()
    elif args.gui:
        launch_gui()
    else:
        # Default ke web API
        debug_mode = not args.no_debug
        launch_web_api(args.host, args.port, debug_mode)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
