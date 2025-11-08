#!/bin/bash
# Enhanced installation script for Smart Buku Keuangan with voice input support

echo "Installing dependencies for Smart Buku Keuangan..."

# Update pip first
pip install --upgrade pip

# Install basic dependencies
pip install -r requirements.txt

# Install PyAudio (which may require system dependencies)
# On some systems, PyAudio requires portaudio to be installed first
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        brew install portaudio
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y portaudio19-dev python3-pyaudio
    elif command -v yum &> /dev/null; then
        sudo yum install -y portaudio-devel
    fi
fi

# Retry installing PyAudio after system dependencies
pip install pyaudio

# Install speech recognition separately in case of issues
pip install SpeechRecognition

echo "Installation complete!"
echo "To run the application, execute: streamlit run app.py"
echo ""
echo "Note: If you encounter issues with PyAudio on macOS, you may need to:"
echo "1. Install Homebrew if not already installed: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
echo "2. Run: brew install portaudio"
echo "3. Then run this script again"
echo ""
echo "For Linux systems, make sure you have the necessary build tools installed."