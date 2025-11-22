import streamlit as st
import speech_recognition as sr
import tempfile
import os
from datetime import datetime, date
import re

# Optional import for PyAudio (required for microphone access)
try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

def voice_to_text():
    """
    Function to convert voice input to text using speech recognition
    """
    # Check if PyAudio is available (required for microphone access)
    if not PYAUDIO_AVAILABLE:
        st.error("Modul PyAudio tidak tersedia. Fitur rekam suara tidak dapat digunakan di lingkungan ini.")
        st.info("Fitur rekam suara memerlukan akses mikrofon yang tidak tersedia di semua platform deploy.")
        return None
    
    r = sr.Recognizer()
    
    # Create a placeholder for status updates
    status_placeholder = st.empty()
    
    try:
        # Use the default microphone as the audio source
        with sr.Microphone() as source:
            status_placeholder.info("Mendengarkan... Silakan bicara sekarang (maksimal 30 detik).")
            
            # Adjust for ambient noise and record
            r.adjust_for_ambient_noise(source)
            try:
                # Listen for audio with longer timeout - this should help with the "too fast" issue
                # Increased timeout from 5 to 15 seconds and phrase_time_limit from 10 to 45 seconds
                # This gives users more time to speak their full transaction
                audio = r.listen(source, timeout=15, phrase_time_limit=45)
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
    except Exception as e:
        status_placeholder.error(f"Gagal mengakses mikrofon: {str(e)}")
        st.info("Fitur rekam suara memerlukan akses mikrofon yang mungkin tidak tersedia di semua platform deploy.")
        return None

def extract_financial_data_from_text(text):
    """
    Function to extract financial data from voice input text - focusing on category and amount only
    """
    if not text:
        return None, None, None, None, None
    
    # Convert to lowercase for easier processing
    text_lower = text.lower()
    
    # Define possible transaction types (categories)
    income_keywords = ['pemasukan', 'penghasilan', 'gaji', 'uang masuk', 'pendapatan', 'income', 'revenue', 'gajian']
    expense_keywords = ['pengeluaran', 'uang keluar', 'belanja', 'biaya', 'expense', 'outgoing', 'makan', 'transport', 'pulsa', 'listrik', 'air', 'sewa', 'tagihan']
    savings_keywords = ['tabungan', 'simpan', 'menabung', 'saving', 'savings', 'deposito', 'investasi']
    debt_keywords = ['hutang', 'pinjaman', 'debit', 'loan', 'cicilan', 'kredit']
    
    # Also define common specific categories
    specific_categories = {
        'makanan': ['makan', 'minum', 'snack', 'kopi', 'nasi', 'mie', 'bakso', 'ayam', 'sate', 'soto', 'gudeg', 'rendang'],
        'transportasi': ['transport', 'bensin', 'angkot', 'ojek', 'grab', 'gojek', 'taxi', 'bus', 'kereta', 'mobil', 'bensin', 'parkir'],
        'hiburan': ['hiburan', 'bioskop', 'game', 'konser', 'wisata', 'rekreasi'],
        'kesehatan': ['kesehatan', 'obat', 'dokter', 'rumah sakit', 'apotek', 'sakit'],
        'pendidikan': ['pendidikan', 'sekolah', 'kuliah', 'buku', 'les', 'kursus', 'spp'],
        'rumah tangga': ['rumah', 'listrik', 'air', 'pulsa', 'sabun', 'deterjen', 'rumah tangga', 'kebutuhan'],
        'belanja': ['belanja', 'shopping', 'pakaian', 'baju', 'celana', 'toped', 'shopee', 'marketplace']
    }
    
    # Determine transaction type first - prioritize explicit type words at the beginning
    transaction_type = "Pemasukan"  # Default
    text_words = text_lower.split()
    
    # Check if the first or second word is the transaction type
    if len(text_words) > 0:
        first_word = text_words[0]
        if first_word in income_keywords:
            transaction_type = "Pemasukan"
        elif first_word in expense_keywords:
            transaction_type = "Pengeluaran"
        elif first_word in savings_keywords:
            transaction_type = "Tabungan"
        elif first_word in debt_keywords:
            transaction_type = "Hutang"
    
    # If still not identified from first word, check the entire text
    if transaction_type == "Pemasukan":  # Default wasn't changed
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
    # Support: Rp 100.000, IDR 1.000.000, 1000000, etc.
    amount_pattern = r'(?:Rp|IDR)?\s*([0-9]+(?:[.][0-9]{3})*(?:[,][0-9]{2})?|[0-9]{1,3}(?:[,][0-9]{3})+|[0-9]+)'
    amount_matches = re.findall(amount_pattern, text)
    
    # Initialize amount
    amount = 0
    
    # Process numeric matches from regex first
    for match in amount_matches:
        raw_amount = match.replace('.', '').replace(',', '')
        try:
            extracted_amount = int(float(raw_amount))
            amount = max(amount, extracted_amount)  # Use the largest amount found
        except ValueError:
            pass

    # Track text used for amount calculation to exclude from description
    amount_text_used = ""
    
    # Process text-based amounts to handle numbers like "lima ratus" (500) or "seribu" (1000)
    # First, check for multipliers 'ribu' or 'juta'
    text_lower = text.lower()
    words = text_lower.split()
    
    def text_to_number(text_part):
        """
        Convert Indonesian text numbers to actual numbers
        Handles: dua puluh lima = 25, tiga ratus = 300, etc.
        """
        parts = text_part.lower().split()
        total = 0
        i = 0
        while i < len(parts):
            part = parts[i]
            
            if part.isdigit():
                # If it's a digit, just multiply by appropriate power if needed
                # or add to total if this is a simple number
                total = int(part)
                i += 1
            elif part in ['nol']:
                total = 0
                i += 1
            elif part in ['satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']:
                total = number_words[part]
                i += 1
            elif part in ['sepuluh', 'sebelas', 'dua belas', 'tiga belas', 'empat belas', 
                          'lima belas', 'enam belas', 'tujuh belas', 'delapan belas', 'sembilan belas']:
                total = number_words[part]
                i += 1
            elif part in ['dua puluh', 'tiga puluh', 'empat puluh', 'lima puluh', 
                          'enam puluh', 'tujuh puluh', 'delapan puluh', 'sembilan puluh']:
                total = number_words[part]
                i += 1
            elif part == 'puluh':
                # Handle cases like "lima puluh" where "puluh" is separate
                if i > 0 and parts[i-1] in ['satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']:
                    # "lima puluh" = 5 * 10 = 50
                    total = number_words[parts[i-1]] * 10
                    i += 1  # Skip the previous word
                    continue
                else:
                    # Just "puluh" alone is 10
                    total = 10
                    i += 1
            elif part == 'belas':
                # Handle cases like "lima belas" where "belas" is separate
                if i > 0 and parts[i-1] in ['se', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']:
                    # "lima belas" = 5 + 10 = 15
                    base = 1 if parts[i-1] == 'se' else number_words[parts[i-1]]
                    total = base + 10
                    i += 1  # Skip the previous word
                    continue
                else:
                    # Just "belas" alone is 10  
                    total = 10
                    i += 1
            elif part == 'ratus':
                # Handle cases like "lima ratus" where "ratus" is separate
                if i > 0 and parts[i-1] in ['satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']:
                    # "lima ratus" = 5 * 100 = 500
                    total = number_words[parts[i-1]] * 100
                    i += 1  # Skip the previous word
                    continue
                elif i > 0 and parts[i-1] == 'se':  # "seratus" as separate "se ratus"
                    total = 100
                    i += 1  # Skip the previous word
                    continue
                else:
                    # Just "ratus" alone is 100
                    total = 100
                    i += 1
            elif part == 'ribu':
                # Handle cases like "ribu" appearing after numbers
                if i > 0 and parts[i-1] in ['satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']:
                    # "lima ribu" = 5 * 1000 = 5000
                    total = number_words[parts[i-1]] * 1000
                    i += 1  # Skip the previous word
                    continue
                elif i > 0 and parts[i-1] == 'se':  # "seribu" as separate "se ribu"
                    total = 1000
                    i += 1  # Skip the previous word
                    continue
                else:
                    # Just "ribu" alone means 1000
                    total = 1000
                    i += 1
            elif part == 'miliar':
                # Handle cases like "miliar" appearing after numbers
                if i > 0 and parts[i-1] in ['satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']:
                    # "lima miliar" = 5 * 1000000000 = 5000000000
                    total = number_words[parts[i-1]] * 1000000000
                    i += 1  # Skip the previous word
                    continue
                elif i > 0 and parts[i-1] == 'se':  # "semiliar" (not common but for completeness)
                    total = 1000000000
                    i += 1  # Skip the previous word
                    continue
                else:
                    # Just "miliar" alone means 1000000000
                    total = 1000000000
                    i += 1
            elif part == 'seratus':
                total = 100
                i += 1
            elif part == 'seribu':
                # Handle "seribu" as a single word meaning 1000
                total = 1000
                i += 1
            else:
                # Handle compound numbers like "dua puluh lima"
                if i + 1 < len(parts):
                    compound = f"{part} {parts[i+1]}"
                    if compound in number_words:
                        total = number_words[compound]
                        i += 2  # Skip both words since we processed as compound
                        continue
                    # Handle special case like "se" + "ribu" = "seribu" (but in split text)
                    elif part == 'se' and parts[i+1] == 'ribu':
                        total = 1000
                        i += 2  # Skip both words
                        continue
                    elif part == 'se' and parts[i+1] == 'ratus':
                        total = 100
                        i += 2  # Skip both words
                        continue
                    # Handle special case like "se" + "miliar" (not common but for completeness)
                    elif part == 'se' and parts[i+1] == 'miliar':
                        total = 1000000000
                        i += 2  # Skip both words
                        continue
                # If we don't recognize the part, just continue
                i += 1
        
        return total

    # Define Indonesian number words including compound numbers
    number_words = {
        'nol': 0, 'satu': 1, 'dua': 2, 'tiga': 3, 'empat': 4, 'lima': 5,
        'enam': 6, 'tujuh': 7, 'delapan': 8, 'sembilan': 9, 'sepuluh': 10,
        'sebelas': 11, 'dua belas': 12, 'tiga belas': 13, 'empat belas': 14,
        'lima belas': 15, 'enam belas': 16, 'tujuh belas': 17, 'delapan belas': 18,
        'sembilan belas': 19, 'dua puluh': 20, 'tiga puluh': 30, 'empat puluh': 40,
        'lima puluh': 50, 'enam puluh': 60, 'tujuh puluh': 70, 'delapan puluh': 80,
        'sembilan puluh': 90, 'seratus': 100, 'ratus': 100, 'puluh': 10, 
        'belas': 10, 'se': 1, 'ribu': 1000, 'seribu': 1000, 'juta': 1000000, 'miliar': 1000000000, 'triliun': 1000000000000
    }

    # First, look for 'ribu' or 'juta' multipliers
    found_multiplier = False
    for i, word in enumerate(words):
        if word in ['ribu', 'juta']:
            multiplier = 1000 if word == 'ribu' else 1000000
            
            # Look for the number part before 'ribu'/'juta'
            # Build the text before the multiplier
            num_text_parts = []
            j = i - 1
            while j >= 0 and words[j] not in ['ribu', 'juta']:
                # Skip transaction type keywords
                if words[j] in income_keywords + expense_keywords + savings_keywords + debt_keywords:
                    j -= 1
                    continue
                # If we encounter a number (digit), add it to the number text
                if words[j].isdigit():
                    num_text_parts.insert(0, words[j])
                    j -= 1
                    continue
                # Otherwise, add the word if it's a number word (like satu, dua, seratus, etc.)
                if words[j] in number_words or words[j] in ['puluh', 'ratus', 'belas']:
                    num_text_parts.insert(0, words[j])
                    j -= 1
                    continue
                break  # Stop if we encounter a non-number word that's not a multiplier or transaction type
            
            if num_text_parts:
                num_text = ' '.join(num_text_parts)
                extracted_num = text_to_number(num_text)
                if extracted_num > 0:
                    calculated_amount = extracted_num * multiplier
                    amount = calculated_amount  # Directly assign this calculated amount
                    found_multiplier = True
                    break
            else:  # If no text before multiplier, check if there's a digit immediately before
                # Handle the case for "pengeluaran 1 juta" where "1" is a digit
                if i > 0 and words[i-1].isdigit():
                    calculated_amount = int(words[i-1]) * multiplier
                    amount = calculated_amount
                    found_multiplier = True
                    break

    # If no multiplier was found, try to process standalone numbers 
    # like "pemasukan lima ratus" or "pengeluaran seribu"
    if not found_multiplier and amount == 0:
        # Process the entire text except transaction type keywords
        num_text_parts = []
        for word in words:
            if word not in income_keywords + expense_keywords + savings_keywords + debt_keywords:
                if word in number_words or word in ['puluh', 'ratus', 'belas', 'ribu', 'juta', 'miliar', 'triliun']:
                    num_text_parts.append(word)
        
        if num_text_parts:
            num_text = ' '.join(num_text_parts)
            extracted_num = text_to_number(num_text)
            if extracted_num > 0:
                amount = extracted_num
                # Track the text used for this amount calculation
                amount_text_used = num_text
    
    # If no numeric amounts were found, try to extract text-based amounts
    if amount == 0:
        text_lower = text.lower()
        words = text_lower.split()
        
        def text_to_number(text_part):
            """
            Convert Indonesian text numbers to actual numbers
            Handles: dua puluh lima = 25, tiga ratus = 300, etc.
            """
            parts = text_part.lower().split()
            total = 0
            current_number = 0
            
            i = 0
            while i < len(parts):
                part = parts[i]
                
                if part.isdigit():
                    current_number = int(part)
                elif part in ['nol']:
                    current_number = 0
                elif part in ['satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']:
                    current_number = number_words[part]
                elif part in ['sepuluh', 'sebelas', 'dua belas', 'tiga belas', 'empat belas', 
                              'lima belas', 'enam belas', 'tujuh belas', 'delapan belas', 'sembilan belas']:
                    current_number = number_words[part]
                elif part in ['dua puluh', 'tiga puluh', 'empat puluh', 'lima puluh', 
                              'enam puluh', 'tujuh puluh', 'delapan puluh', 'sembilan puluh']:
                    current_number = number_words[part]
                elif part == 'puluh':
                    # Handle cases like "dua puluh lima" where "puluh" is separate
                    if i > 0 and parts[i-1] in ['satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']:
                        current_number = number_words[parts[i-1]] * 10
                        total = current_number  # Update total since we found tens
                        i += 1  # Skip the previous word
                        continue
                elif part == 'belas':
                    # Handle cases like "lima belas" where "belas" is separate
                    if i > 0 and parts[i-1] in ['se', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']:
                        base = 1 if parts[i-1] == 'se' else number_words[parts[i-1]]
                        current_number = base + 10
                        total = current_number  # Update total since we found teens
                        i += 1  # Skip the previous word
                        continue
                elif part == 'ratus':
                    # Handle cases like "tiga ratus" where "ratus" is separate
                    if i > 0 and parts[i-1] in ['satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']:
                        current_number = number_words[parts[i-1]] * 100
                        total = current_number  # Update total since we found hundreds
                        i += 1  # Skip the previous word
                        continue
                elif part == 'ribu':
                    # Handle cases like "lima ribu" where "ribu" is separate
                    if i > 0 and parts[i-1] in ['satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']:
                        current_number = number_words[parts[i-1]] * 1000
                        total = current_number  # Update total since we found thousands
                        i += 1  # Skip the previous word
                        continue
                    else:
                        # Just "ribu" alone means 1000
                        current_number = 1000
                        total = current_number
                elif part == 'miliar':
                    # Handle cases like "lima miliar" where "miliar" is separate
                    if i > 0 and parts[i-1] in ['satu', 'dua', 'tiga', 'empat', 'lima', 'enam', 'tujuh', 'delapan', 'sembilan']:
                        current_number = number_words[parts[i-1]] * 1000000000
                        total = current_number  # Update total since we found billions
                        i += 1  # Skip the previous word
                        continue
                    else:
                        # Just "miliar" alone means 1000000000
                        current_number = 1000000000
                        total = current_number
                elif part == 'seratus':
                    current_number = 100
                
                # Handle compound numbers like "dua puluh lima"
                if i + 1 < len(parts):
                    compound = f"{part} {parts[i+1]}"
                    if compound in number_words:
                        current_number = number_words[compound]
                        i += 1  # Skip next word since we processed it as compound
                
                total += current_number
                current_number = 0
                i += 1
            
            return total

        # Define Indonesian number words including compound numbers
        number_words = {
            'nol': 0, 'satu': 1, 'dua': 2, 'tiga': 3, 'empat': 4, 'lima': 5,
            'enam': 6, 'tujuh': 7, 'delapan': 8, 'sembilan': 9, 'sepuluh': 10,
            'sebelas': 11, 'dua belas': 12, 'tiga belas': 13, 'empat belas': 14,
            'lima belas': 15, 'enam belas': 16, 'tujuh belas': 17, 'delapan belas': 18,
            'sembilan belas': 19, 'dua puluh': 20, 'tiga puluh': 30, 'empat puluh': 40,
            'lima puluh': 50, 'enam puluh': 60, 'tujuh puluh': 70, 'delapan puluh': 80,
            'sembilan puluh': 90, 'seratus': 100, 'ratus': 100, 'puluh': 10, 
            'belas': 10, 'se': 1, 'ribu': 1000, 'seribu': 1000, 'juta': 1000000, 'miliar': 1000000000, 'triliun': 1000000000000
        }

        # Look for 'triliun', 'miliar', 'juta', or 'ribu' in the text - process in descending order of magnitude
        # This allows handling complex numbers like "satu juta dua ratus lima puluh empat ribu tiga ratus"
        multipliers_found = []
        for i, word in enumerate(words):
            if word in ['ribu', 'juta', 'miliar', 'triliun']:
                if word == 'ribu':
                    multiplier = 1000
                elif word == 'juta':
                    multiplier = 1000000
                elif word == 'miliar':
                    multiplier = 1000000000
                else:  # 'triliun'
                    multiplier = 1000000000000
                
                # Look for the number part before 'ribu'/'juta'/'miliar'/'triliun'
                # Build the text before the multiplier
                num_text_parts = []
                j = i - 1
                while j >= 0 and words[j] not in ['ribu', 'juta', 'miliar', 'triliun']:
                    # Skip transaction type keywords
                    if words[j] in income_keywords + expense_keywords + savings_keywords + debt_keywords:
                        j -= 1
                        continue
                    # If we encounter a number (digit), add it to the number text
                    if words[j].isdigit():
                        num_text_parts.insert(0, words[j])
                        j -= 1
                        continue
                    # Otherwise, add the word if it's a number word (like satu, dua, seratus, etc.)
                    if words[j] in number_words or words[j] in ['puluh', 'ratus', 'belas']:
                        num_text_parts.insert(0, words[j])
                        j -= 1
                        continue
                    break  # Stop if we encounter a non-number word that's not a multiplier or transaction type
                
                multiplier_info = {
                    'position': i,
                    'multiplier': multiplier,
                    'num_text_parts': num_text_parts,
                    'word': word
                }
                multipliers_found.append(multiplier_info)
        
        # Process multipliers from right to left (smallest to largest magnitude) to handle complex numbers
        if multipliers_found:
            multipliers_found.sort(key=lambda x: x['position'], reverse=True)  # Sort from right to left
            
            total_amount = 0
            used_text_parts = []
            
            for mult_info in multipliers_found:
                num_text_parts = mult_info['num_text_parts']
                multiplier = mult_info['multiplier']
                word = mult_info['word']
                
                if num_text_parts:
                    num_text = ' '.join(num_text_parts)
                    extracted_num = text_to_number(num_text)
                    if extracted_num > 0:
                        calculated_part = extracted_num * multiplier
                        total_amount += calculated_part
                        used_text_parts.append(num_text + " " + word)
                else:  # If no text before multiplier, check if there's a digit immediately before
                    # Handle the case for "pengeluaran 1 juta" where "1" is a digit
                    i = mult_info['position']
                    if i > 0 and words[i-1].isdigit():
                        calculated_part = int(words[i-1]) * multiplier
                        total_amount += calculated_part
                        used_text_parts.append(words[i-1] + " " + word)
            
            if total_amount > 0:
                amount = total_amount
                # Track all text used for amount calculation
                amount_text_used = " ".join(used_text_parts)

    # Identify category from specific categories mentioned in the text
    category = transaction_type  # Default to transaction type
    
    # Check for specific categories first
    found_specific_category = False
    for cat_name, cat_keywords in specific_categories.items():
        for keyword in cat_keywords:
            if keyword in text_lower:
                category = cat_name.title()  # Use the specific category name
                found_specific_category = True
                break
        if found_specific_category:
            break

    # If no specific category is found, try to extract a general category from the text
    if not found_specific_category:
        # Look for words that might indicate a category (usually nouns that follow the transaction type)
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in income_keywords + expense_keywords + savings_keywords + debt_keywords:
                # The next few words might contain the category
                if i + 1 < len(words):
                    potential_category = ' '.join(words[i+1:i+3])  # Take next 1-2 words as category
                    # Clean up the potential category
                    potential_category = re.sub(r'(?:Rp|IDR)?\s*[0-9.,]+', '', potential_category, flags=re.IGNORECASE)
                    potential_category = ' '.join(potential_category.split()).strip().title()
                    if potential_category and len(potential_category) > 1:
                        category = potential_category
                        break

    # Extract item/description by identifying and preserving the descriptive part
    # Remove the amount from the text to get the description part
    text_without_amount = text
    for match in amount_matches:
        text_without_amount = text_without_amount.replace(match, '', 1)
    
    # Remove text-based amounts that were used for calculation
    if amount_text_used:
        text_without_amount = text_without_amount.replace(amount_text_used, '', 1)
    
    # Remove currency indicators
    text_without_amount = re.sub(r'(?:Rp|IDR)\s*', '', text_without_amount, flags=re.IGNORECASE)
    
    # Remove transaction type keywords but keep the rest as description
    description = text_without_amount.strip()
    for keyword in income_keywords + expense_keywords + savings_keywords + debt_keywords:
        # Remove the keyword and any surrounding spaces
        description = re.sub(r'\b' + re.escape(keyword) + r'\b\s*', ' ', description, flags=re.IGNORECASE)
    
    # Clean up extra whitespace and capitalize
    description = ' '.join(description.split()).strip().title()
    
    # If description is empty or just spaces, use a default description based on category
    if not description or description.isspace():
        if category and category != transaction_type:
            description = category
        else:
            description = "Transaksi Suara"
    
    # For notes, we'll use the original text
    notes = text.strip()
    
    return transaction_type, amount, description, category, notes

def voice_input_interface():
    """
    Function to create the voice input interface for financial data
    """
    st.subheader("🎤 Input Suara untuk Data Keuangan")
    
    # Add instructions for voice input
    with st.expander("ℹ️ Petunjuk Input Suara", expanded=True):
        st.markdown("""
        **Cara menggunakan input suara:**
        1. Tekan tombol "🔊 Rekam Suara" 
        2. Sebutkan **KATEGORI TRANSAKSI** dan **JUMLAH UANG** dalam bahasa Indonesia:
           - **Kategori** (makanan, transportasi, belanja, pendidikan, dll.)
           - **Jumlah uang** (misalnya: satu juta, seratus ribu, lima puluh ribu)
        
        **Contoh:** "makan di warung, seratus ribu" atau "beli rumah satu miliar"
        
        📝 **Tips:** Bicaralah dengan jelas dan perlahan. Sistem akan merekam hingga 30 detik atau hingga jeda terdeteksi.
        
        ⚠️ Pastikan lingkungan sekitar cukup tenang dan suara Anda jelas terdengar.
        """)
        
    # Check if PyAudio is available
    if not PYAUDIO_AVAILABLE:
        st.warning("Fitur rekam suara tidak tersedia di lingkungan ini karena modul PyAudio tidak ditemkan.")
        st.info("Untuk menggunakan fitur rekam suara, aplikasi harus dijalankan secara lokal dengan PyAudio terinstal.")
        # Provide a text input as fallback
        with st.form("voice_input_fallback"):
            voice_text = st.text_area("Masukkan transaksi dalam bentuk teks (sebagai simulasi suara):", 
                                    placeholder="Contoh: pengeluaran beli rumah satu miliar")
            submit = st.form_submit_button("Proses Teks sebagai Suara")
            
            if submit and voice_text:
                st.success(f"Memproses teks sebagai input suara: {voice_text}")
                
                # Extract financial data from text input (simulating voice input)
                transaction_type, amount, extracted_description, category, notes = extract_financial_data_from_text(voice_text)
                
                # Display extracted data for confirmation and editing
                if transaction_type:
                    st.subheader("📊 Data Terekam - Konfirmasi dan Edit:")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        selected_type = st.selectbox("Jenis Transaksi", 
                                                   ["Pemasukan", "Pengeluaran", "Tabungan", "Hutang", "Lainnya"],
                                                   index=["Pemasukan", "Pengeluaran", "Tabungan", "Hutang", "Lainnya"].index(transaction_type) if transaction_type in ["Pemasukan", "Pengeluaran", "Tabungan", "Hutang", "Lainnya"] else 0)
                    with col2:
                        entered_amount = st.number_input("Jumlah (Rp)", min_value=0, value=amount, format="%d")
                    
                    entered_description = st.text_input("Deskripsi Item", value=extracted_description)
                    # Use the original voice input as notes
                    entered_notes = st.text_area("Catatan Tambahan", value=notes, help="Catatan akan diisi otomatis dari input suara")
                    
                    # Use today's date
                    from datetime import date
                    entered_date = date.today()
                    
                    # Confirmation button to save
                    if st.button("✅ Simpan Transaksi", type="primary"):
                        return {
                            'date': entered_date,
                            'type': selected_type,
                            'amount': entered_amount,
                            'description': entered_description,
                            'notes': entered_notes
                        }
                else:
                    st.error("Tidak dapat mengekstrak data keuangan dari teks yang dimasukkan.")
        return None
    
    # Create button for voice recording (only when PyAudio is available)
    if st.button("🔊 Rekam Suara"):
        st.info("📝 Petunjuk: Bicaralah dengan jelas dan perlahan. Sistem akan merekam hingga 30 detik atau hingga jeda terdeteksi.")
        with st.spinner("Menyiapkan mikrofon..."):
            # Capture voice input
            voice_text = voice_to_text()
            
            if voice_text:
                st.success(f"Berhasil merekam suara: {voice_text}")
                
                # Extract financial data from voice input
                transaction_type, amount, extracted_description, category, notes = extract_financial_data_from_text(voice_text)
                
                # Display extracted data for confirmation and editing
                if transaction_type:
                    st.subheader("📊 Data Terekam - Konfirmasi dan Edit:")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        selected_type = st.selectbox("Jenis Transaksi", 
                                                   ["Pemasukan", "Pengeluaran", "Tabungan", "Hutang", "Lainnya"],
                                                   index=["Pemasukan", "Pengeluaran", "Tabungan", "Hutang", "Lainnya"].index(transaction_type) if transaction_type in ["Pemasukan", "Pengeluaran", "Tabungan", "Hutang", "Lainnya"] else 0)
                    with col2:
                        entered_amount = st.number_input("Jumlah (Rp)", min_value=0, value=amount, format="%d")
                    
                    entered_description = st.text_input("Deskripsi Item", value=extracted_description)
                    # Use the original voice input as notes
                    entered_notes = st.text_area("Catatan Tambahan", value=notes, help="Catatan akan diisi otomatis dari input suara")
                    
                    # Use today's date
                    from datetime import date
                    entered_date = date.today()
                    
                    # Confirmation button to save
                    if st.button("✅ Simpan Transaksi", type="primary"):
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
                st.info("💡 Tips: Bicaralah dengan jelas, lebih perlahan, dan pastikan lingkungan sekitar cukup tenang.")
    
    return None

def voice_input_form():
    """
    Function to create a full voice input form with fallback to manual input
    """
    # Create tabs for voice input and manual input
    voice_tab, manual_tab = st.tabs(["🎤 Input Suara", "✏️ Input Manual"])
    
    with voice_tab:
        # Add instructions for voice input
        with st.expander("ℹ️  Input Suara", expanded=True):
            st.markdown("""
            **Cara menggunakan input suara:**
            1. Tekan tombol "🔊 Rekam Suara" 
            2. Sebutkan **KATEGORI TRANSAKSI** dan **JUMLAH UANG** dalam bahasa Indonesia:
               - **Kategori** (makanan, transportasi, belanja, pendidikan, dll.)
               - **Jumlah uang** (misalnya: satu juta, seratus ribu, lima puluh ribu)
            
            **Contoh:** "makan di warung, seratus ribu" atau "beli rumah satu miliar"
            
            📝 **Tips:** Bicaralah dengan jelas dan perlahan. Sistem akan merekam hingga 45 detik.
            
            ⚠️ Pastikan lingkungan sekitar cukup tenang dan suara Anda jelas terdengar.
            """)
        
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