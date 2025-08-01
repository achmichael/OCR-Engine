#!/bin/bash

# OCR ML Engine - Installation Script
# ===================================
# Script untuk menginstall semua dependencies yang diperlukan

echo "🚀 OCR ML Engine - Installation Script"
echo "======================================"

# Function untuk check command existence
check_command() {
    if command -v $1 &> /dev/null; then
        echo "✅ $1 is installed"
        return 0
    else
        echo "❌ $1 is not installed"
        return 1
    fi
}

# Function untuk install on different OS
install_tesseract() {
    echo "🔧 Installing Tesseract OCR..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "Detected Linux system"
        sudo apt update
        sudo apt install -y tesseract-ocr
        sudo apt install -y tesseract-ocr-eng  # English
        sudo apt install -y tesseract-ocr-ind  # Indonesian
        sudo apt install -y poppler-utils      # For PDF processing
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "Detected macOS system"
        if check_command "brew"; then
            brew install tesseract
            brew install tesseract-lang
            brew install poppler
        else
            echo "❌ Homebrew not found. Please install Homebrew first:"
            echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
        
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows (Git Bash/Cygwin)
        echo "Detected Windows system"
        echo "⚠️  For Windows, please manually install:"
        echo "   1. Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki"
        echo "   2. Add Tesseract to your PATH"
        echo "   3. Download poppler for Windows: https://poppler.freedesktop.org/"
        
    else
        echo "❌ Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Main installation process
echo ""
echo "📋 Checking system requirements..."

# Check Python
if check_command "python3"; then
    PYTHON_CMD="python3"
elif check_command "python"; then
    PYTHON_CMD="python"
else
    echo "❌ Python not found. Please install Python 3.7+ first"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "🐍 Python version: $PYTHON_VERSION"

# Check pip
if check_command "pip3"; then
    PIP_CMD="pip3"
elif check_command "pip"; then
    PIP_CMD="pip"
else
    echo "❌ pip not found. Please install pip first"
    exit 1
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
$PIP_CMD install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Check and install Tesseract
echo ""
if ! check_command "tesseract"; then
    echo "🔧 Tesseract not found. Installing..."
    install_tesseract
else
    echo "✅ Tesseract is already installed"
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n1)
    echo "   Version: $TESSERACT_VERSION"
fi

# Verify installation
echo ""
echo "🔍 Verifying installation..."

# Test Python imports
echo "Testing Python imports..."
$PYTHON_CMD -c "
import cv2
print('✅ OpenCV imported successfully')
import numpy as np  
print('✅ NumPy imported successfully')
import PIL
print('✅ PIL imported successfully')
try:
    import pytesseract
    print('✅ PyTesseract imported successfully')
except ImportError:
    print('⚠️ PyTesseract import failed')
try:
    import easyocr
    print('✅ EasyOCR imported successfully')
except ImportError:
    print('⚠️ EasyOCR import failed - this is optional')
"

# Test Tesseract
if check_command "tesseract"; then
    echo "Testing Tesseract..."
    tesseract --list-langs 2>/dev/null | head -5
    echo "✅ Tesseract is working"
fi

# Test OCR Engine
echo ""
echo "🧪 Testing OCR Engine..."
$PYTHON_CMD -c "
try:
    from ocr_engine import OCREngine
    print('✅ OCR Engine imported successfully')
    # Test initialization
    ocr = OCREngine(use_gpu=False, languages=['en'])
    print('✅ OCR Engine initialized successfully')
except Exception as e:
    print(f'❌ OCR Engine test failed: {e}')
"

echo ""
echo "🎉 Installation completed!"
echo ""
echo "📚 Next steps:"
echo "   1. Test the installation: python examples.py"
echo "   2. Try CLI interface: python ocr_cli.py --help"  
echo "   3. Start GUI application: python ocr_gui.py"
echo "   4. Start web API: python web_api.py"
echo ""
echo "📖 For detailed usage instructions, see README.md"
