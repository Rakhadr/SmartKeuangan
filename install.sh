#!/bin/bash
# Installation script for Smart Buku Keuangan

echo "Installing dependencies for Smart Buku Keuangan..."

# Install Python dependencies
pip install -r requirements.txt

echo "Installation complete!"
echo "To run the application, execute: streamlit run app.py"