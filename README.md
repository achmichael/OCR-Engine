# OCR ML Engine

Sebuah sistem Machine Learning berbasis OCR (Optical Character Recognition) yang canggih untuk mengenali dan mengekstrak teks dari gambar dan file PDF.

## Fitur Utama

### 🔍 **Multi-Engine OCR**
- **Tesseract OCR**: Engine OCR yang powerful dengan konfigurasi optimal
- **EasyOCR**: Neural network-based OCR dengan support multi-bahasa
- **Automatic Best Selection**: Sistem otomatis memilih hasil terbaik berdasarkan confidence score

### 📸 **Image Processing**
- **Advanced Preprocessing**: 3 level enhancement (Basic, Medium, Aggressive)
- **Noise Reduction**: Gaussian blur untuk mengurangi noise
- **Contrast Enhancement**: Histogram equalization untuk meningkatkan kontras
- **Adaptive Thresholding**: Binarization yang optimal untuk berbagai kondisi
- **Morphological Operations**: Cleaning dan enhancement struktur karakter

### 📄 **PDF Support**
- **Direct Text Extraction**: Extract teks langsung dari PDF yang sudah berisi text
- **OCR Fallback**: Konversi PDF ke images untuk OCR jika direct extraction gagal
- **Page Range Selection**: Proses halaman tertentu saja
- **High-Quality Conversion**: Konversi dengan DPI tinggi untuk akurasi optimal

### 🌐 **Multiple Interfaces**
- **Command Line Interface (CLI)**: Untuk automasi dan batch processing
- **Web API (REST)**: Untuk integrasi dengan aplikasi lain
- **Graphical User Interface (GUI)**: Interface user-friendly dengan tkinter

### 🚀 **Performance Features**
- **Batch Processing**: Proses multiple files sekaligus
- **Threading Support**: Background processing untuk responsivitas
- **Progress Tracking**: Real-time progress monitoring
- **Detailed Logging**: Comprehensive logging untuk debugging

## Struktur Project

```
OCR/
├── ocr_engine.py          # Core OCR engine dengan multiple backends
├── pdf_processor.py       # PDF processing dan conversion
├── web_api.py            # Flask-based REST API
├── ocr_cli.py            # Command line interface
├── ocr_gui.py            # Tkinter-based GUI
├── requirements.txt       # Python dependencies
├── README.md             # Dokumentasi ini
├── examples/             # Contoh penggunaan
│   ├── sample_images/    # Sample images untuk testing
│   └── sample_pdfs/      # Sample PDFs untuk testing
├── uploads/              # Temporary uploads (auto-created)
├── results/              # OCR results (auto-created)
└── logs/                 # Log files (auto-created)
```

## Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd OCR
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

#### Windows:
1. Download Tesseract dari: https://github.com/UB-Mannheim/tesseract/wiki
2. Install dan tambahkan ke PATH
3. Atau install via chocolatey: `choco install tesseract`

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-ind  # Untuk bahasa Indonesia
```

#### macOS:
```bash
brew install tesseract
brew install tesseract-lang  # Untuk bahasa tambahan
```

### 4. Verify Installation
```bash
python ocr_engine.py  # Test core engine
```

## Penggunaan

### 1. Command Line Interface (CLI)

#### OCR Single Image
```bash
# Basic usage
python ocr_cli.py -i input.jpg -o result.txt

# Dengan enhancement level aggressive
python ocr_cli.py -i input.jpg -e 3 -o result.txt

# Output dalam format JSON
python ocr_cli.py -i input.jpg -o result.json --format json
```

#### OCR Multiple Images
```bash
# Batch processing dengan pattern
python ocr_cli.py -i "images/*.jpg" -o results/ --format json

# Batch processing dari directory
python ocr_cli.py -b images/ -o results/ -v
```

#### OCR PDF Files
```bash
# OCR full PDF
python ocr_cli.py -p document.pdf -o extracted.txt

# OCR specific page range
python ocr_cli.py -p document.pdf --page-range 1 10 -o output.txt

# Try direct extraction first
python ocr_cli.py -p document.pdf --try-direct -o output.txt
```

#### Advanced Options
```bash
# Dengan verbose logging dan GPU
python ocr_cli.py -i input.jpg -o result.txt -v --gpu

# Custom language dan engine
python ocr_cli.py -i input.jpg --languages "en,id,fr" --engine tesseract

# Cleanup temporary files
python ocr_cli.py -b images/ -o results/ --cleanup
```

### 2. Web API

#### Start Web Server
```bash
python web_api.py
```

Server akan berjalan di `http://localhost:5000`

#### API Endpoints

##### GET `/` - API Information
```bash
curl http://localhost:5000/
```

##### GET `/health` - Health Check
```bash
curl http://localhost:5000/health
```

##### POST `/ocr/image` - Single Image OCR
```bash
curl -X POST \
  -F "file=@image.jpg" \
  -F "enhancement_level=2" \
  http://localhost:5000/ocr/image
```

##### POST `/ocr/batch` - Batch Image OCR
```bash
curl -X POST \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "enhancement_level=3" \
  http://localhost:5000/ocr/batch
```

##### POST `/ocr/pdf` - PDF OCR
```bash
curl -X POST \
  -F "file=@document.pdf" \
  -F "page_start=1" \
  -F "page_end=5" \
  http://localhost:5000/ocr/pdf
```

##### GET `/results/<result_id>` - Get Detailed Results
```bash
curl http://localhost:5000/results/your-result-id
```

### 3. Graphical User Interface (GUI)

```bash
python ocr_gui.py
```

GUI Features:
- **File Selection**: Drag & drop atau browse files
- **Settings Panel**: Konfigurasi enhancement level, engine, languages
- **Real-time Progress**: Progress bar dan status updates
- **Results Display**: Scrollable text area dengan hasil OCR
- **Export Options**: Save results ke file atau copy ke clipboard

### 4. Python API Integration

```python
from ocr_engine import OCREngine
from pdf_processor import PDFProcessor

# Initialize OCR Engine
ocr = OCREngine(use_gpu=False, languages=['en', 'id'])

# Process single image
result = ocr.process_image_file('image.jpg', enhancement_level=2)
print(f"Extracted Text: {result['combined_text']}")

# Process PDF
pdf_processor = PDFProcessor(dpi=300)
pdf_result = pdf_processor.extract_text_from_pdf_direct('document.pdf')

if pdf_result['text']:
    print("Direct extraction successful!")
else:
    # Use OCR fallback
    image_arrays = pdf_processor.convert_pdf_pages_to_arrays('document.pdf')
    for i, img_array in enumerate(image_arrays):
        processed = ocr.preprocess_image(img_array, 2)
        text_result = ocr.extract_text_tesseract(processed)
        print(f"Page {i+1}: {text_result['text']}")
```

## Konfigurasi Advanced

### 1. Enhancement Levels

#### Level 1 (Basic)
- Gaussian blur untuk noise reduction
- Histogram equalization
- Basic morphological operations

#### Level 2 (Medium) - **Recommended**
- Semua fitur Level 1
- Adaptive thresholding
- Dilation untuk character enhancement

#### Level 3 (Aggressive)
- Semua fitur Level 2
- Edge detection dan enhancement
- Lebih intensive processing (slower tapi lebih akurat)

### 2. OCR Engine Selection

#### Tesseract
- **Best for**: Dokumen formal, text dengan font standar
- **Kelebihan**: Akurasi tinggi untuk text berkualitas baik
- **Kekurangan**: Sensitif terhadap noise dan orientasi

#### EasyOCR
- **Best for**: Handwriting, text dengan background kompleks
- **Kelebihan**: Robust terhadap noise, support multi-orientasi
- **Kekurangan**: Sedikit lebih lambat

#### Both (Auto-Select)
- **Best for**: Mixed content, unknown document types
- **Behavior**: Jalankan kedua engine dan pilih hasil terbaik

### 3. Language Support

Bahasa yang didukung:
- **en**: English
- **id**: Bahasa Indonesia
- **zh**: Chinese
- **ja**: Japanese
- **ko**: Korean
- **th**: Thai
- **vi**: Vietnamese
- **ar**: Arabic
- **hi**: Hindi
- **fr**: French
- **de**: German
- **es**: Spanish
- **pt**: Portuguese
- **ru**: Russian

## Tips Optimasi

### 1. Image Quality
- **Resolution**: Minimum 300 DPI untuk hasil optimal
- **Format**: PNG lebih baik dari JPEG untuk text
- **Contrast**: Pastikan kontras yang baik antara text dan background
- **Orientation**: Text harus tegak (gunakan image rotation jika perlu)

### 2. PDF Processing
- **Direct Extraction**: Selalu coba direct extraction dulu untuk PDF digital
- **Page Range**: Proses halaman tertentu untuk dokumen besar
- **DPI Setting**: 300 DPI balance antara quality dan speed, 600 DPI untuk akurasi maksimal

### 3. Performance
- **Batch Size**: Process 10-20 images per batch untuk memory efficiency
- **Threading**: GUI dan Web API menggunakan background threading
- **Cleanup**: Enable cleanup untuk temporary files pada production

## Troubleshooting

### Common Issues

#### 1. Tesseract Not Found
```
Error: Tesseract not found in PATH
```
**Solution**: Install Tesseract dan pastikan ada di system PATH

#### 2. Import Error
```
ImportError: No module named 'cv2'
```
**Solution**: Install OpenCV dengan `pip install opencv-python`

#### 3. PDF Conversion Failed
```
Error: Failed to convert PDF to images
```
**Solution**: Install poppler dengan `apt install poppler-utils` (Linux) atau download poppler binaries (Windows)

#### 4. Memory Error
```
MemoryError: Unable to allocate array
```
**Solution**: Reduce image resolution atau process dalam smaller batches

#### 5. Low Accuracy
- Coba enhancement level yang lebih tinggi
- Periksa kualitas image input
- Gunakan preprocessing manual jika perlu
- Coba engine yang berbeda

### Debug Mode

Enable verbose logging untuk troubleshooting:

```bash
# CLI
python ocr_cli.py -i input.jpg -o result.txt -v

# Check log file
tail -f ocr_cli.log
```

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push branch: `git push origin feature-name`
5. Submit Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Tesseract OCR**: Google's OCR engine
- **EasyOCR**: JaidedAI's neural network OCR
- **OpenCV**: Computer vision library
- **Flask**: Web framework untuk API
- **tkinter**: GUI framework
