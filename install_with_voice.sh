#!/bin/bash
# Enhanced installation script for Smart Buku Keuangan with voice input support

echo "Installing dependencies for Smart Buku Keuangan..."

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
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt-get &> /dev/null; then
        echo "Installing tesseract via apt..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr
    elif command -v yum &> /dev/null; then
        echo "Installing tesseract via yum..."
        sudo yum install -y tesseract
    else
        echo "Please install tesseract for your system to use image input functionality."
    fi
fi

# Install PyAudio (which may require system dependencies)
# On some systems, PyAudio requires portaudio to be installed first
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        echo "Installing portaudio via Homebrew..."
        brew install portaudio
    else
        echo "Homebrew not found. PyAudio may fail to install on macOS without portaudio."
        echo "Consider installing Homebrew: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo "Then run: brew install portaudio"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt-get &> /dev/null; then
        echo "Installing portaudio and pyaudio development dependencies via apt..."
        sudo apt-get update
        sudo apt-get install -y portaudio19-dev python3-pyaudio
    elif command -v yum &> /dev/null; then
        echo "Installing portaudio development dependencies via yum..."
        sudo yum install -y portaudio-devel
    else
        echo "Please install portaudio development libraries for your system to build PyAudio."
    fi
fi

# Retry installing PyAudio after system dependencies
echo "Installing PyAudio..."
pip install pyaudio || echo "PyAudio installation failed. This is expected on some deployment platforms like Streamlit Sharing."

# Install speech recognition
echo "Installing SpeechRecognition..."
pip install SpeechRecognition

echo "Installation complete!"
echo "To run the application locally, execute: streamlit run app.py"
echo ""
echo "Note: On platforms without microphone access (like Streamlit Sharing),"
echo "voice input will gracefully degrade to text input mode."
echo ""
echo "If you encounter issues with PyAudio on macOS, you may need to:"
echo "1. Install Homebrew if not already installed: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
echo "2. Run: brew install portaudio"
echo "3. Then run this script again"
echo ""
echo "For Linux systems, make sure you have the necessary build tools installed."