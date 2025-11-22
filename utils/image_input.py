"""
Image-based receipt processing module for Keuangan-Pintar
This module uses OCR and ML to extract financial information from receipts
"""
import streamlit as st
import numpy as np
from PIL import Image
import re
from datetime import datetime, date
import tempfile
import os

# Try to import cv2 and pytesseract with error handling for deployment environments
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    pytesseract = None
    TESSERACT_AVAILABLE = False

# Image input availability depends on both cv2 and pytesseract
IMAGE_INPUT_AVAILABLE = CV2_AVAILABLE and TESSERACT_AVAILABLE

def extract_financial_data_from_image(image_path):
    """
    Extract financial data from receipt image using OCR
    """
    if not IMAGE_INPUT_AVAILABLE:
        if not CV2_AVAILABLE:
            st.error("Modul OpenCV (cv2) tidak tersedia. Fitur pemrosesan struk tidak dapat digunakan.")
            st.info("Fitur ini membutuhkan OpenCV dan Tesseract OCR untuk berfungsi.")
            return None, None, None, None, None
        elif not TESSERACT_AVAILABLE:
            st.error("Modul OCR (pytesseract) tidak tersedia. Fitur pemrosesan struk tidak dapat digunakan.")
            st.info("Untuk menggunakannya, install pytesseract dan Tesseract OCR di sistem Anda.")
            return None, None, None, None, None
    
    try:
        # Check if tesseract command is available
        import subprocess
        try:
            subprocess.run(['tesseract', '--version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            st.error("Tesseract OCR command line tool tidak ditemukan. Silakan install Tesseract di sistem Anda.")
            st.info("Pada macOS: brew install tesseract")
            st.info("Pada Ubuntu: sudo apt-get install tesseract-ocr")
            return None, None, None, None, None
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            return None, None, None, None, None
        
        # Preprocess image for better OCR
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get image with only black and white
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Use pytesseract to extract text from image
        # Try Indonesian first, but fall back to English if language pack is not available
        try:
            text = pytesseract.image_to_string(thresh, lang='ind')
        except:
            # If Indonesian language pack is not available, use English
            try:
                text = pytesseract.image_to_string(thresh, lang='eng')
            except:
                # If no language packs are available, use default (English)
                text = pytesseract.image_to_string(thresh)
        
        # Extract financial information from text
        amount = extract_amount_from_text(text)
        description = extract_description_from_text(text)
        transaction_type = determine_transaction_type(text)
        date_from_receipt = extract_date_from_text(text)
        
        # Return with category (using "Struk" as the category for receipt-based entries)
        return transaction_type, amount, description, "Struk", date_from_receipt
    
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None, None, None, None, None

def extract_amount_from_text(text):
    """
    Extract amount from receipt text using regex patterns
    """
    # Common Indonesian currency patterns
    patterns = [
        r'(?:Rp|IDR)?[\s.]*([0-9]{1,3}(?:[,.][0-9]{3})*(?:[,.][0-9]{2})?)',
        r'(?:total|jumlah|grand total|subtotal|amount)[\s:]*Rp\s*([0-9.,]+)',
        r'(?:total|jumlah|grand total|subtotal|amount)[\s:]*([0-9.,]+)\s*IDR',
    ]
    
    amounts = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Clean the amount string
            clean_amount = re.sub(r'[.,]', '', match)  # Remove formatting
            try:
                amount = int(float(clean_amount))
                amounts.append(amount)
            except ValueError:
                continue
    
    # Return the largest amount found, or 0 if none found
    return max(amounts) if amounts else 0

def extract_description_from_text(text):
    """
    Extract description from receipt text
    """
    lines = text.split('\n')
    description = ""
    
    # Look for store name, items, or receipt title
    for line in lines:
        line = line.strip()
        if line and len(line) > 2 and len(line) < 50:
            # Skip lines that look like phone numbers, addresses, or totals
            if not re.match(r'^[\d\-\+\(\)\s]+$', line) and \
               not re.match(r'^(?:total|jumlah|grand|subtotal|bayar)', line.lower()) and \
               not re.search(r'(?:Rp|IDR)', line, re.IGNORECASE):
                description = line
                break
    
    if not description:
        # Default to the first meaningful line
        for line in lines:
            line = line.strip()
            if line and len(line) > 5 and len(line) < 100:
                description = line
                break
    
    return description.title() if description else "Transaksi dari Struk"

def determine_transaction_type(text):
    """
    Determine transaction type based on receipt content
    """
    text_lower = text.lower()
    
    # Keywords for expense
    expense_keywords = [
        'warung', 'toko', 'minimarket', 'supermarket', 'mall', 'shop', 'store',
        'restaurant', 'cafe', 'kopi', 'makan', 'minum', 'food', 'meal',
        'bensin', 'pertamina', 'shell', 'pengisian', 'bahan bakar',
        'pulsa', 'paket data', 'telepon', 'listrik', 'air', 'tagihan',
        'laundry', 'service', 'jasa', 'transportasi', 'ojek', 'grab', 'gojek'
    ]
    
    # Keywords for income
    income_keywords = [
        'gaji', 'salary', 'income', 'pendapatan', 'bayaran', 'uang',
        'transfer', 'diterima', 'received', 'pembayaran', 'payment'
    ]
    
    # Check for expense indicators
    for keyword in expense_keywords:
        if keyword in text_lower:
            return "Pengeluaran"
    
    # Check for income indicators  
    for keyword in income_keywords:
        if keyword in text_lower:
            return "Pemasukan"
    
    # Default to expense since most receipts are for expenses
    return "Pengeluaran"

def extract_date_from_text(text):
    """
    Extract date from receipt text
    """
    # Common date patterns
    patterns = [
        r'(\d{2}[/-]\d{2}[/-]\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
        r'(\d{4}[/-]\d{2}[/-]\d{2})',  # YYYY/MM/DD or YYYY-MM-DD
        r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|Mei|Jun|Jul|Agu|Sep|Okt|Nov|Des)[a-z]*\s+\d{4})',  # Day Month Year
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                # Try to parse the date
                if '/' in match or '-' in match:
                    # Handle DD/MM/YYYY or YYYY/MM/DD
                    if len(match.split('/')[0]) == 4 or len(match.split('-')[0]) == 4:
                        parsed_date = datetime.strptime(match.replace('-', '/'), '%Y/%m/%d').date()
                    else:
                        parsed_date = datetime.strptime(match.replace('-', '/'), '%d/%m/%Y').date()
                else:
                    # Handle Day Month Year format
                    parsed_date = datetime.strptime(match, '%d %b %Y').date()
                
                # Validate date is reasonable (not too far in future or past)
                today = date.today()
                if parsed_date <= today and parsed_date.year >= 2020:
                    return parsed_date
            except ValueError:
                continue
    
    # If no valid date found, return today's date
    return date.today()

def image_input_interface():
    """
    Interface for image-based receipt input
    """
    if not TESSERACT_AVAILABLE:
        st.warning("Modul OCR (pytesseract) tidak tersedia. Fitur pemrosesan struk tidak dapat digunakan.")
        st.info("Untuk menggunakannya:")
        st.info("1. Install pytesseract: pip install pytesseract")
        st.info("2. Install Tesseract OCR di sistem Anda:")
        st.info("   - macOS: brew install tesseract")
        st.info("   - Ubuntu: sudo apt-get install tesseract-ocr")
        st.info("   - CentOS: sudo yum install tesseract")
        return None
    
    st.subheader("📸 Input Struk untuk Data Keuangan")
    
    with st.expander("ℹ️ Petunjuk Input Struk", expanded=True):
        st.markdown("""
        **Cara menggunakan input struk:**
        1. Siapkan foto struk pembelian/transaksi yang jelas
        2. Unggah file gambar (JPG, PNG, JPEG)
        3. Sistem akan otomatis membaca informasi dari struk
        4. Edit data jika perlu dan simpan
        
        📝 **Tips:** Pastikan struk terlihat jelas, tidak blur, dan cukup cahaya
        """)
    
    # File uploader for receipt images
    uploaded_file = st.file_uploader(
        "Upload Struk Pembelian", 
        type=['jpg', 'jpeg', 'png'],
        help="Unggah foto struk dalam format JPG, JPEG, atau PNG"
    )
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Struk yang Diunggah", use_container_width=True)
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_path = tmp_file.name
        
        try:
            # Extract financial data from the image
            with st.spinner("Membaca informasi dari struk..."):
                transaction_type, amount, description, category, extracted_date = extract_financial_data_from_image(temp_path)
            
            if transaction_type is not None:
                st.success("Berhasil membaca informasi dari struk!")
                
                # Display extracted data for confirmation and editing
                st.subheader("📊 Data Terekam - Konfirmasi dan Edit:")
                
                col1, col2 = st.columns(2)
                with col1:
                    selected_type = st.selectbox(
                        "Jenis Transaksi", 
                        ["Pemasukan", "Pengeluaran", "Tabungan", "Hutang", "Lainnya"],
                        index=["Pemasukan", "Pengeluaran", "Tabungan", "Hutang", "Lainnya"].index(transaction_type) 
                        if transaction_type in ["Pemasukan", "Pengeluaran", "Tabungan", "Hutang", "Lainnya"] else 1
                    )
                with col2:
                    entered_amount = st.number_input("Jumlah (Rp)", min_value=0, value=amount if amount > 0 else 0, format="%d")
                
                entered_description = st.text_input("Deskripsi Item", value=description if description else "")
                
                # Date selection (use extracted date as default if valid)
                entered_date = st.date_input("Tanggal", value=extracted_date if extracted_date else date.today())
                
                # Notes field
                entered_notes = st.text_area(
                    "Catatan Tambahan", 
                    value=f"Data diambil dari struk: {uploaded_file.name}",
                    help="Catatan tambahan tentang transaksi"
                )
                
                # Confirmation button to save
                if st.button("✅ Simpan Transaksi dari Struk", type="primary", use_container_width=True):
                    return {
                        'date': entered_date,
                        'type': selected_type,
                        'amount': entered_amount,
                        'description': entered_description,
                        'notes': entered_notes
                    }
            else:
                st.error("Tidak dapat membaca informasi dari struk. Silakan coba dengan gambar yang lebih jelas.")
                st.info("💡 Tips: Pastikan struk terlihat jelas, tidak blur, dan cukup cahaya. Sudut gambar juga penting untuk pembacaan yang akurat.")
        
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses gambar: {str(e)}")
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    return None