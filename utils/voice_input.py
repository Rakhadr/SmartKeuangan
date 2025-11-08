import streamlit as st
import speech_recognition as sr
import tempfile
import os
from datetime import datetime, date
import re

def voice_to_text():
    """
    Function to convert voice input to text using speech recognition
    """
    r = sr.Recognizer()
    
    # Create a placeholder for status updates
    status_placeholder = st.empty()
    
    # Use the default microphone as the audio source
    with sr.Microphone() as source:
        status_placeholder.info("Mendengarkan... Silakan bicara sekarang.")
        
        # Adjust for ambient noise and record
        r.adjust_for_ambient_noise(source)
        try:
            # Listen for audio with timeout
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
            status_placeholder.info("Mengenali suara...")
            
            # Try to recognize the speech using Google's speech recognition
            text = r.recognize_google(audio, language="id-ID")  # Using Indonesian language
            status_placeholder.success("Berhasil mengenali suara!")
            return text
        except sr.WaitTimeoutError:
            status_placeholder.error("Tidak ada suara terdeteksi dalam waktu yang ditentukan.")
            return None
        except sr.UnknownValueError:
            status_placeholder.error("Tidak dapat mengenali suara. Silakan coba lagi.")
            return None
        except sr.RequestError as e:
            status_placeholder.error(f"Kesalahan pada layanan pengenalan suara: {str(e)}")
            return None

def extract_financial_data_from_text(text):
    """
    Function to extract financial data from voice input text
    """
    if not text:
        return None, None, None, None, None
    
    # Convert to lowercase for easier processing
    text_lower = text.lower()
    
    # Define possible transaction types
    income_keywords = ['pemasukan', 'penghasilan', 'gaji', 'uang masuk', 'pendapatan', 'income', 'revenue']
    expense_keywords = ['pengeluaran', 'uang keluar', 'belanja', 'biaya', 'expense', 'outgoing']
    savings_keywords = ['tabungan', 'simpan', 'menabung', 'saving', 'savings']
    debt_keywords = ['hutang', 'pinjaman', 'debit', 'loan']
    
    # Determine transaction type
    transaction_type = "Pemasukan"  # Default
    for keyword in income_keywords:
        if keyword in text_lower:
            transaction_type = "Pemasukan"
            break
    for keyword in expense_keywords:
        if keyword in text_lower:
            transaction_type = "Pengeluaran"
            break
    for keyword in savings_keywords:
        if keyword in text_lower:
            transaction_type = "Tabungan"
            break
    for keyword in debt_keywords:
        if keyword in text_lower:
            transaction_type = "Hutang"
            break
    
    # Extract amount using regex (numbers with common Indonesian formats)
    amount_pattern = r'(?:Rp|IDR)?\s*([0-9]+(?:[.][0-9]{3})*(?:[,][0-9]{2})?|[0-9]{1,3}(?:[,][0-9]{3})+|[0-9]+)'
    amount_matches = re.findall(amount_pattern, text)
    
    amount = 0
    if amount_matches:
        # Take the first numeric value found
        raw_amount = amount_matches[0].replace('.', '').replace(',', '')
        try:
            amount = int(float(raw_amount))
        except ValueError:
            amount = 0
    
    # Extract item/description by identifying and preserving the descriptive part
    # Remove the amount from the text to get the description part
    text_without_amount = text
    for match in amount_matches:
        text_without_amount = text_without_amount.replace(match, '', 1)
    
    # Remove currency indicators
    text_without_amount = re.sub(r'(?:Rp|IDR)\s*', '', text_without_amount, flags=re.IGNORECASE)
    
    # Remove transaction type keywords but keep the rest as description
    description = text_without_amount.strip()
    for keyword in income_keywords + expense_keywords + savings_keywords + debt_keywords:
        # Remove the keyword and any surrounding spaces
        description = re.sub(r'\b' + re.escape(keyword) + r'\b\s*', ' ', description, flags=re.IGNORECASE)
    
    # Clean up extra whitespace and capitalize
    description = ' '.join(description.split()).strip().title()
    
    # If description is empty or just spaces, use a default description
    if not description or description.isspace():
        description = "Transaksi Suara"
    
    # For category, we'll use a default based on transaction type
    category = transaction_type
    
    # For notes, we'll use the original text
    notes = text.strip()
    
    return transaction_type, amount, description, category, notes

def voice_input_interface():
    """
    Function to create the voice input interface for financial data
    """
    st.subheader("🎤 Input Suara untuk Data Keuangan")
    
    # Create button for voice recording
    if st.button("🔊 Rekam Suara"):
        with st.spinner("Menyiapkan mikrofon..."):
            # Capture voice input
            voice_text = voice_to_text()
            
            if voice_text:
                st.success(f"Berhasil merekam suara: {voice_text}")
                
                # Extract financial data from voice input
                transaction_type, amount, description, category, notes = extract_financial_data_from_text(voice_text)
                
                # Display extracted data
                if transaction_type:
                    st.subheader("📊 Data Terekam:")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        selected_type = st.selectbox("Jenis Transaksi", 
                                                   ["Pemasukan", "Pengeluaran", "Tabungan", "Hutang", "Lainnya"],
                                                   index=["Pemasukan", "Pengeluaran", "Tabungan", "Hutang", "Lainnya"].index(transaction_type) if transaction_type in ["Pemasukan", "Pengeluaran", "Tabungan", "Hutang", "Lainnya"] else 0)
                    with col2:
                        entered_amount = st.number_input("Jumlah (Rp)", min_value=0, value=amount, format="%d")
                    
                    entered_description = st.text_input("Deskripsi Item", value=description)
                    entered_notes = st.text_area("Catatan Tambahan", value=notes)
                    
                    # Use today's date
                    entered_date = date.today()
                    
                    return {
                        'date': entered_date,
                        'type': selected_type,
                        'amount': entered_amount,
                        'description': entered_description,
                        'notes': entered_notes
                    }
                else:
                    st.error("Tidak dapat mengekstrak data keuangan dari suara yang direkam.")
            else:
                st.error("Gagal merekam suara. Silakan coba lagi.")
    
    return None

def voice_input_form():
    """
    Function to create a full voice input form with fallback to manual input
    """
    # Create tabs for voice input and manual input
    voice_tab, manual_tab = st.tabs(["🎤 Input Suara", "✏️ Input Manual"])
    
    with voice_tab:
        voice_data = voice_input_interface()
    
    with manual_tab:
        with st.form("manual_input", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                tanggal = st.date_input("Tanggal", date.today())
                jenis = st.selectbox("Jenis Transaksi", ["Pemasukan", "Pengeluaran", "Tabungan", "Hutang", "Lainnya"])
            with col2:
                nilai = st.number_input("Jumlah (Rp)", min_value=0, format="%d")
            
            item = st.text_input("Deskripsi Item")
            catatan = st.text_area("Catatan Tambahan")
            
            manual_submit = st.form_submit_button("Simpan Transaksi 💰", use_container_width=True, type="primary")
            
            if manual_submit:
                return {
                    'date': tanggal,
                    'type': jenis,
                    'amount': nilai,
                    'description': item,
                    'notes': catatan
                }
    
    # Return voice data if it was captured, otherwise return None
    if voice_data:
        # User can still modify voice-extracted data, so we'll return it if it exists
        return voice_data
    elif 'voice_data' in st.session_state and st.session_state.voice_data:
        # If voice data was captured but user modified it manually, use the modified version
        return st.session_state.voice_data
    
    return None