import io
import pandas as pd
from fpdf import FPDF

def export_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def export_to_pdf(df):
    # Create a temporary file name
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_filename = temp_file.name

    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)

        # Judul
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, txt="Laporan Keuangan", ln=True, align='C')
        pdf.ln(5)

        # Check if dataframe is empty
        if df.empty:
            pdf.set_font("Arial", size=10)
            pdf.cell(200, 10, txt="Tidak ada data untuk diekspor", ln=True, align='C')
        else:
            # Header
            pdf.set_font("Arial", style='B', size=10)
            col_widths = [30, 30, 40, 30, 60]
            headers = df.columns.tolist()
            for i, h in enumerate(headers):
                pdf.cell(col_widths[i], 10, str(h), border=1)
            pdf.ln()

            # Rows
            pdf.set_font("Arial", size=10)
            for index, row in df.iterrows():
                for i, item in enumerate(row):
                    # Ensure the item can be converted to string properly
                    cell_content = str(item) if pd.notna(item) else ""
                    pdf.cell(col_widths[i], 10, cell_content, border=1)
                pdf.ln()

        # Output to the temporary file
        pdf.output(temp_filename)
        
        # Read the file content as bytes
        with open(temp_filename, 'rb') as f:
            pdf_bytes = f.read()
        
        return pdf_bytes
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
