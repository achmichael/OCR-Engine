@echo off
REM OCR ML Engine - Windows Installation Script
REM ============================================
REM Script untuk menginstall dependencies di Windows

echo 🚀 OCR ML Engine - Windows Installation Script
echo ===============================================

REM Check Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python is installed
    python --version
) else (
    echo ❌ Python not found. Please install Python 3.7+ first
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check pip
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ pip is installed
) else (
    echo ❌ pip not found. Please install pip first
    pause
    exit /b 1
)

echo.
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo ✅ Python dependencies installed successfully
) else (
    echo ❌ Failed to install Python dependencies
    pause
    exit /b 1
)

REM Check Tesseract
echo.
tesseract --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Tesseract is installed
    tesseract --version
) else (
    echo ❌ Tesseract not found
    echo.
    echo 🔧 Installing Tesseract OCR...
    echo Please follow these steps:
    echo.
    echo 1. Download Tesseract installer from:
    echo    https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo 2. Run the installer and follow the installation wizard
    echo.
    echo 3. During installation, make sure to:
    echo    - Select "Add to PATH" option
    echo    - Install additional language packs (English, Indonesian)
    echo.
    echo 4. After installation, restart this script
    echo.
    echo Alternative installation via Chocolatey:
    echo    choco install tesseract
    echo.
    pause
    echo Continuing without Tesseract... (some features may not work)
)

REM Install poppler for PDF processing
echo.
echo 📄 Setting up PDF processing...
echo.
echo For PDF processing, you need poppler utilities:
echo 1. Download poppler for Windows from:
echo    https://poppler.freedesktop.org/
echo.
echo 2. Extract to a folder (e.g., C:\poppler)
echo.
echo 3. Add the bin folder to your PATH:
echo    C:\poppler\bin
echo.
echo Alternative: Use conda to install poppler:
echo    conda install -c conda-forge poppler

REM Verify installation
echo.
echo 🔍 Verifying installation...

REM Test Python imports
echo Testing Python imports...
python -c "import cv2; print('✅ OpenCV imported successfully')" 2>nul || echo "⚠️ OpenCV import failed"
python -c "import numpy; print('✅ NumPy imported successfully')" 2>nul || echo "⚠️ NumPy import failed"
python -c "import PIL; print('✅ PIL imported successfully')" 2>nul || echo "⚠️ PIL import failed"
python -c "import pytesseract; print('✅ PyTesseract imported successfully')" 2>nul || echo "⚠️ PyTesseract import failed"
python -c "import easyocr; print('✅ EasyOCR imported successfully')" 2>nul || echo "⚠️ EasyOCR import failed (optional)"

REM Test OCR Engine
echo.
echo 🧪 Testing OCR Engine...
python -c "from ocr_engine import OCREngine; print('✅ OCR Engine imported successfully'); ocr = OCREngine(use_gpu=False, languages=['en']); print('✅ OCR Engine initialized successfully')" 2>nul || echo "❌ OCR Engine test failed"

echo.
echo 🎉 Installation completed!
echo.
echo 📚 Next steps:
echo    1. Test the installation: python examples.py
echo    2. Try CLI interface: python ocr_cli.py --help
echo    3. Start GUI application: python ocr_gui.py
echo    4. Start web API: python web_api.py
echo.
echo 📖 For detailed usage instructions, see README.md
echo.

REM Optional: Create desktop shortcuts
set /p create_shortcuts="Create desktop shortcuts? (y/n): "
if /i "%create_shortcuts%"=="y" (
    echo Creating desktop shortcuts...
    
    REM Create shortcut for GUI
    echo Set oWS = WScript.CreateObject("WScript.Shell") > "%temp%\shortcut.vbs"
    echo sLinkFile = "%USERPROFILE%\Desktop\OCR GUI.lnk" >> "%temp%\shortcut.vbs"
    echo Set oLink = oWS.CreateShortcut(sLinkFile) >> "%temp%\shortcut.vbs"
    echo oLink.TargetPath = "python" >> "%temp%\shortcut.vbs"
    echo oLink.Arguments = "%CD%\ocr_gui.py" >> "%temp%\shortcut.vbs"
    echo oLink.WorkingDirectory = "%CD%" >> "%temp%\shortcut.vbs"
    echo oLink.Save >> "%temp%\shortcut.vbs"
    cscript "%temp%\shortcut.vbs" >nul
    del "%temp%\shortcut.vbs"
    
    echo ✅ Desktop shortcuts created
)

pause
