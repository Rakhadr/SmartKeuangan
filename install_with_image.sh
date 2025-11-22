#!/bin/bash
# Installation script for Smart Buku Keuangan with image processing support

echo "Installing dependencies for Smart Buku Keuangan with image processing support..."

# Update pip first
pip install --upgrade pip

# Install basic dependencies
pip install -r requirements.txt

# Install OpenCV for image processing
pip install opencv-python

# Install Tesseract for OCR (if not already installed)
# On macOS with Homebrew: brew install tesseract
# On Ubuntu/Debian: sudo apt-get install tesseract-ocr
# On CentOS/RHEL: sudo yum install tesseract
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        echo "Installing tesseract via Homebrew..."
        brew install tesseract
    else
        echo "Tesseract not found. Please install it manually: brew install tesseract"
        echo "You can install Homebrew with: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt-get &> /dev/null; then
        echo "Installing tesseract via apt..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr libtesseract-dev
    elif command -v yum &> /dev/null; then
        echo "Installing tesseract via yum..."
        sudo yum install -y tesseract
    else
        echo "Please install tesseract for your system to use image input functionality."
    fi
fi

# Install pytesseract Python package
pip install pytesseract

echo "Installation complete!"
echo "To run the application locally, execute: streamlit run app.py"
echo ""
echo "Note: For image input functionality to work properly, you need:"
echo "1. Tesseract OCR installed on your system (tesseract command available)"
echo "2. The Python packages opencv-python and pytesseract"
echo ""
echo "If you encounter issues with image processing:"
echo "1. Make sure tesseract is installed and in your PATH"
echo "2. On macOS: brew install tesseract"
echo "3. On Ubuntu/Debian: sudo apt-get install tesseract-ocr"
echo "4. On CentOS/RHEL: sudo yum install tesseract"