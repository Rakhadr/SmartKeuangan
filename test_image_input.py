#!/usr/bin/env python3
"""
Test script for image input functionality
"""
import os
import sys

def test_image_input_import():
    """Test that the image input module can be imported"""
    print("Testing image input module import...")
    
    try:
        from utils.image_input import image_input_interface
        print("✓ Image input interface imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import image input interface: {e}")
        return False
    
    try:
        from utils.image_input import extract_financial_data_from_image
        print("✓ Image financial data extraction function imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import image financial data extraction function: {e}")
        return False
    
    return True

def test_dependencies():
    """Test that required dependencies are available"""
    print("\nTesting required dependencies...")
    
    dependencies = [
        ("cv2", "opencv-python"),
        ("PIL", "Pillow"), 
        ("pytesseract", "pytesseract")
    ]
    
    missing_deps = []
    for module_name, package_name in dependencies:
        try:
            if module_name == "cv2":
                import cv2
            elif module_name == "PIL":
                from PIL import Image
            elif module_name == "pytesseract":
                import pytesseract
            print(f"✓ {module_name} ({package_name}) is available")
        except ImportError:
            print(f"✗ {module_name} ({package_name}) is NOT available")
            missing_deps.append(package_name)
    
    if missing_deps:
        print(f"\nMissing dependencies: {', '.join(missing_deps)}")
        print("Install them using: pip install " + ' '.join(missing_deps))
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality if dependencies are available"""
    print("\nTesting basic functionality...")
    
    try:
        import cv2
        import numpy as np
        from PIL import Image
        
        # Create a simple test image (in memory)
        # Create a blank image to test image processing functions
        test_img_array = np.ones((100, 300, 3), dtype=np.uint8) * 255  # White background
        
        # Write some simple test text
        cv2.putText(test_img_array, "TOKO SERBA ADA", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.putText(test_img_array, "Beli Makanan Rp 25.000", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        cv2.putText(test_img_array, "Tanggal: 15/05/2023", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Save to temporary file
        temp_path = "/tmp/test_receipt.jpg"
        cv2.imwrite(temp_path, test_img_array)
        
        # Test the extraction function
        from utils.image_input import extract_financial_data_from_image
        transaction_type, amount, description, date_from_receipt = extract_financial_data_from_image(temp_path)
        
        print(f"Test extraction results:")
        print(f"  Transaction type: {transaction_type}")
        print(f"  Amount: {amount}")
        print(f"  Description: {description}")
        print(f"  Date: {date_from_receipt}")
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        print("✓ Basic functionality test completed")
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Testing Image Input Functionality for Keuangan-Pintar\n")
    print("="*60)
    
    success = True
    
    # Test imports
    if not test_image_input_import():
        success = False
    
    # Test dependencies
    if not test_dependencies():
        success = False
    
    # Test basic functionality
    if not test_basic_functionality():
        success = False
    
    print("\n" + "="*60)
    if success:
        print("✓ All tests passed! Image input functionality is ready.")
        print("\nTo use the image input feature:")
        print("1. Make sure Tesseract OCR is installed on your system")
        print("2. Run the main application with: streamlit run app.py")
        print("3. Navigate to 'Input Data' section")
        print("4. Use the '📸 Struk' tab to upload receipt images")
    else:
        print("✗ Some tests failed. Please check the installation requirements.")
    
    return success

if __name__ == "__main__":
    main()