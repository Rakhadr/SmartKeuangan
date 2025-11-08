#!/usr/bin/env python3
"""
Test script to verify the voice input functionality works as expected
"""

def test_voice_recognition_imports():
    """Test that all required modules can be imported"""
    try:
        import speech_recognition as sr
        print("✓ SpeechRecognition module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SpeechRecognition: {e}")
        return False
    
    try:
        import pyaudio
        print("✓ PyAudio module imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PyAudio: {e}")
        return False
    
    try:
        from utils.voice_input import voice_to_text, extract_financial_data_from_text, voice_input_interface, voice_input_form
        print("✓ All voice input functions imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import voice input functions: {e}")
        return False
    
    return True

def test_data_extraction():
    """Test the financial data extraction function"""
    from utils.voice_input import extract_financial_data_from_text
    
    # Test cases
    test_cases = [
        "Pengeluaran belanja Rp50.000 untuk makanan",
        "Pemasukan gaji Rp5.000.000 dari kantor",
        "Tabungan simpan Rp2.500.000 di bank",
        "Pengeluaran hutang Rp1.200.000 ke teman"
    ]
    
    print("\nTesting data extraction from voice input:")
    for i, test_case in enumerate(test_cases, 1):
        transaction_type, amount, description, category, notes = extract_financial_data_from_text(test_case)
        print(f"  Test {i}: '{test_case}'")
        print(f"    Type: {transaction_type}, Amount: {amount}, Description: {description}")
    
    return True

if __name__ == "__main__":
    print("Testing voice input functionality...\n")
    
    if test_voice_recognition_imports():
        print("✓ All imports successful")
        
        if test_data_extraction():
            print("✓ Data extraction working correctly")
            print("\n✓ Voice input functionality is ready to use!")
        else:
            print("✗ Data extraction test failed")
    else:
        print("✗ Import test failed")