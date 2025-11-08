import streamlit as st
import pandas as pd
import sqlite3
import datetime
import calendar

# Try to import plotly with error handling for deployment environments
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None
    make_subplots = None
    st.error("Modul plotly tidak tersedia. Beberapa fitur grafik mungkin tidak berfungsi.")

from utils.helpers import init_db, save_transaction, get_transactions, verify_user, create_user
from utils.export import export_to_csv, export_to_pdf
from utils.ai import generate_financial_advice

# Import voice input with error handling
try:
    from utils.voice_input import voice_input_form
    VOICE_INPUT_AVAILABLE = True
except ImportError as e:
    st.error(f"Gagal mengimpor modul voice input: {e}")
    VOICE_INPUT_AVAILABLE = False
    # Define a fallback function
    def voice_input_form():
        st.error("Modul voice input tidak tersedia.")
        return None

# ----------------------------
# Inisialisasi DB dan Session
# ----------------------------
init_db()

# Initialize session state variables with proper defaults
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'email' not in st.session_state:
    st.session_state.email = ""
if 'nama' not in st.session_state:
    st.session_state.nama = ""
if 'kategori_pengguna' not in st.session_state:
    st.session_state.kategori_pengguna = None
if 'transaction_saved' not in st.session_state:
    st.session_state.transaction_saved = False
if 'user_exists' not in st.session_state:
    st.session_state.user_exists = False
if 'show_login' not in st.session_state:
    st.session_state.show_login = True  # True for login, False for registration
if 'user_nama' not in st.session_state:
    st.session_state.user_nama = ""
if 'registration_success' not in st.session_state:
    st.session_state.registration_success = False
if 'menu' not in st.session_state:
    st.session_state.menu = "Beranda"

# Validate user session after initialization, if email exists but user isn't logged in
from utils.helpers import get_user_info

if st.session_state.email and not st.session_state.logged_in:
    user_info = get_user_info(st.session_state.email)
    if user_info:
        # User is valid, ensure they stay logged in
        st.session_state.logged_in = True
        st.session_state.nama = user_info[0]
        st.session_state.kategori_pengguna = user_info[1]
        # Preserve the current menu if it exists
        if 'menu' not in st.session_state:
            st.session_state.menu = "Beranda"

# ----------------------------
# UI - LOGIN DAN PILIHAN USER
# ----------------------------
st.set_page_config(
    page_title="Smart Buku Keuangan",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Custom CSS to improve the UI
st.markdown("""
<style>
    /* Hide Streamlit's default menu and footer */
    #MainMenu {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }
    header[data-testid="stHeader"] {
        visibility: hidden;
    }
    
    .main-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
        text-align: center;
    }
    .sub-header {
        font-size: 1.3rem;
        color: #34495e;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .finance-card {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .positive {
        color: #2ecc71;
    }
    .negative {
        color: #e74c3c;
    }
    .advice-box {
        background-color: #f0f7ff;
        padding: 1.2rem;
        border-radius: 8px;
        border-left: 5px solid #3498db;
    }
    .data-table {
        background-color: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .small-text {
        font-size: 0.9rem;
    }
    
    /* Mobile adjustments */
    @media (max-width: 600px) {
        .block-container {
            padding-top: 3rem;
        }
    }
</style>
""", unsafe_allow_html=True)

if not st.session_state.logged_in:
    # Title for non-logged in users
    st.markdown('<h1 class="main-header">🔒 Smart Buku Keuangan</h1>', unsafe_allow_html=True)
    
    # Tabs for login and registration
    login_tab, register_tab = st.tabs(["🔐 Masuk", "📝 Daftar"])
    
    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Alamat Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            submit_login = st.form_submit_button("Masuk 📝", use_container_width=True, type="primary")

            if submit_login and email and password:
                # Verify user credentials
                user_info = verify_user(email, password)
                if user_info:
                    nama, kategori_pengguna = user_info
                    st.session_state.logged_in = True
                    st.session_state.nama = nama
                    st.session_state.email = email
                    st.session_state.kategori_pengguna = kategori_pengguna
                    st.session_state.menu = "Beranda"  # Set default menu to Beranda
                    st.success(f"🎉 Selamat datang kembali, {nama}!")
                    st.rerun()
                else:
                    st.error("Email atau password salah!")
    
    # Check if registration was successful and show success message
    if 'registration_success' in st.session_state and st.session_state.registration_success:
        st.success("🎉 Berhasil Daftar, Silahkan Login")
        if st.button("Ke Halaman Login", use_container_width=True, type="primary"):
            st.session_state.show_login = True
            st.session_state.registration_success = False
            st.rerun()
    else:
        with register_tab:
            with st.form("register_form"):
                nama = st.text_input("Nama Lengkap", key="reg_nama")
                email = st.text_input("Alamat Email", key="reg_email")
                password = st.text_input("Password", type="password", key="reg_password")
                kategori = st.selectbox("Kategori Pengguna", 
                    ["Keluarga", "Pribadi", "Siswa/Mahasiswa", "Pedagang", "UMKM", "Pengusaha", "Pebisnis"], key="reg_kategori")
                submit_register = st.form_submit_button("Daftar Sekarang", use_container_width=True, type="secondary")

                if submit_register and nama and email and password:
                    # Create new user
                    from utils.helpers import create_user
                    if create_user(nama, email, password, kategori):
                        st.session_state.registration_success = True
                        st.rerun()
                    else:
                        st.error("Email sudah terdaftar! Silakan gunakan email lain.")

else:
    # Sidebar with title, user information and navigation
    with st.sidebar:
        # Compact title in sidebar
        st.markdown('<h1 class="main-header">📒 Smart Keuangan</h1>', unsafe_allow_html=True)
        
        # User information
        st.markdown(f"""
        <div class="small-text">
            <p><strong>👤 {st.session_state.nama}</strong></p>
            <p><strong>Kategori:</strong> {st.session_state.kategori_pengguna}</p>
            <p><strong>Email:</strong> {st.session_state.email}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Navigation buttons
        st.subheader("Navigasi")
        if st.button("🏠 Beranda", use_container_width=True):
            st.session_state.menu = "Beranda"
        if st.button("➕ Input Data", use_container_width=True):
            st.session_state.menu = "Input Data"
        if st.button("📋 Lihat Catatan", use_container_width=True):
            st.session_state.menu = "Lihat Catatan"
        if st.button("📊 Grafik & Insight", use_container_width=True):
            st.session_state.menu = "Grafik & Insight"
        if st.button("🤖 AI Assistant", use_container_width=True):
            st.session_state.menu = "AI Assistant"
        if st.button("📤 Export Data", use_container_width=True):
            st.session_state.menu = "Export Data"
        
        st.divider()  # Add separator before logout
        
        # Logout button
        if st.button("🔒 Logout", use_container_width=True, type="secondary"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        menu = st.session_state.menu

    # Main content area
    
    # Floating bottom navigation for mobile
    if st.session_state.logged_in:
        # Mobile burger menu for navigation using Streamlit expander
        if st.session_state.logged_in:
            # Use Streamlit's expander as a mobile menu
            with st.popover("☰", use_container_width=False):
                st.write("Navigasi")
                
                if st.button("🏠 Beranda", use_container_width=True):
                    st.session_state.menu = "Beranda"
                    st.rerun()
                
                if st.button("➕ Input Data", use_container_width=True):
                    st.session_state.menu = "Input Data"
                    st.rerun()
                
                if st.button("📋 Lihat Catatan", use_container_width=True):
                    st.session_state.menu = "Lihat Catatan"
                    st.rerun()
                
                if st.button("📊 Grafik & Insight", use_container_width=True):
                    st.session_state.menu = "Grafik & Insight"
                    st.rerun()
                
                if st.button("🤖 AI Assistant", use_container_width=True):
                    st.session_state.menu = "AI Assistant"
                    st.rerun()
                
                if st.button("📤 Export Data", use_container_width=True):
                    st.session_state.menu = "Export Data"
                    st.rerun()
                
                if st.button("🔒 Logout", use_container_width=True):
                    # Clear session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()

    # Main content area
    if menu == "Beranda":
        st.markdown('<h1 class="sub-header">🏠 Beranda</h1>', unsafe_allow_html=True)
        
        # Get user's transaction data
        df = get_transactions(st.session_state.email)
        
        # Display summary metrics
        if not df.empty:
            # Calculate financial metrics
            total_pemasukan = df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum()
            total_pengeluaran = df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
            total_tabungan = df[df['Jenis'] == 'Tabungan']['Jumlah'].sum()
            saldo = total_pemasukan - total_pengeluaran
            
            # Display metrics in cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f'<div class="metric-card"><h3>Rp{total_pemasukan:,.0f}</h3><p>Pemasukan</p></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-card"><h3 class="negative">Rp{total_pengeluaran:,.0f}</h3><p>Pengeluaran</p></div>', unsafe_allow_html=True)
            with col3:
                st.markdown(f'<div class="metric-card"><h3 class="positive">Rp{total_tabungan:,.0f}</h3><p>Tabungan</p></div>', unsafe_allow_html=True)
            with col4:
                color_class = "positive" if saldo >= 0 else "negative"
                st.markdown(f'<div class="metric-card"><h3 class="{color_class}">Rp{saldo:,.0f}</h3><p>Saldo</p></div>', unsafe_allow_html=True)
            
            # Recent transactions preview
            st.subheader("Transaksi Terbaru")
            st.dataframe(df.tail(5), use_container_width=True)
            
        else:
            st.info("Belum ada data keuangan.")
            # Button that redirects to input data page
            if st.button("➕ Input Data Keuangan", use_container_width=True, type="primary"):
                st.session_state.menu = "Input Data"
                st.rerun()

    elif menu == "Input Data":
        st.markdown('<h1 class="sub-header">➕ Input Data Keuangan</h1>', unsafe_allow_html=True)
        kategori = st.session_state.kategori_pengguna
        
        # Get input data using voice input form that includes both voice and manual options
        input_data = voice_input_form()
        
        # If data was captured (either from voice or manual), save it
        if input_data:
            # Save the transaction
            save_transaction(
                st.session_state.email, 
                input_data['date'], 
                kategori, 
                input_data['type'], 
                input_data['description'], 
                input_data['amount'], 
                input_data['notes']
            )
            st.session_state.transaction_saved = True
            st.success("✅ Data berhasil disimpan!")

        # Add button to see all records after successful save (outside the form)
        if st.session_state.transaction_saved:
            if st.button("📋 Lihat Catatan Keuangan", use_container_width=True, type="secondary"):
                st.session_state.menu = "Lihat Catatan"
                st.rerun()

    elif menu == "Lihat Catatan":
        st.markdown('<h1 class="sub-header">📋 Riwayat Catatan Keuangan</h1>', unsafe_allow_html=True)
        df = get_transactions(st.session_state.email)
        
        if df.empty:
            st.info("Belum ada data keuangan.")
        else:
            # Summary section
            total_pemasukan = df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum()
            total_pengeluaran = df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
            saldo = total_pemasukan - total_pengeluaran
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Pemasukan", f"Rp{total_pemasukan:,.0f}")
            with col2:
                st.metric("Pengeluaran", f"Rp{total_pengeluaran:,.0f}")
            with col3:
                color = "inverse" if saldo < 0 else "normal"
                st.metric("Saldo", f"Rp{saldo:,.0f}", delta_color=color)
            
            # Data display with search and filters
            st.subheader("Detail Transaksi")
            st.dataframe(df, use_container_width=True, height=500)

    elif menu == "Grafik & Insight":
        st.markdown('<h1 class="sub-header">📊 Analisis Keuangan</h1>', unsafe_allow_html=True)
        
        # Show success message if a transaction was just saved
        if st.session_state.get('transaction_saved', False):
            st.success("✅ Data berhasil disimpan")
            st.session_state.transaction_saved = False  # Reset the flag
        
        df = get_transactions(st.session_state.email)
        if df.empty:
            st.info("Belum ada data untuk dianalisis.")
        else:
            df["Tanggal"] = pd.to_datetime(df["Tanggal"])
            
            # Set default date range to current month
            today = datetime.date.today()
            first_day_current_month = today.replace(day=1)
            
            # Calculate the last day of current month
            if today.month == 12:
                last_day_current_month = today.replace(day=31)
            else:
                # Get first day of next month, then subtract one day
                days_in_month = calendar.monthrange(today.year, today.month)[1]
                last_day_current_month = today.replace(day=days_in_month)
            
            # Default to current month (1st to last day of month)
            start_date_default = first_day_current_month
            end_date_default = last_day_current_month
            
            # Time range filter - default to current month
            date_range = st.date_input("Pilih Rentang Tanggal", value=[start_date_default, end_date_default])
            
            # Filter data based on date selection
            if len(date_range) == 2:
                start_date, end_date = date_range
                filtered_df = df[(df["Tanggal"] >= pd.Timestamp(start_date)) & (df["Tanggal"] <= pd.Timestamp(end_date))]
            else:
                filtered_df = df
            
            if not filtered_df.empty:
                # Calculate financial metrics
                total_pemasukan = filtered_df[filtered_df['Jenis'] == 'Pemasukan']['Jumlah'].sum()
                total_pengeluaran = filtered_df[filtered_df['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
                saldo = total_pemasukan - total_pengeluaran
                
                # Display metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Pemasukan", f"Rp{total_pemasukan:,.0f}")
                with col2:
                    st.metric("Total Pengeluaran", f"Rp{total_pengeluaran:,.0f}")
                with col3:
                    st.metric("Saldo", f"Rp{saldo:,.0f}")
                
                if PLOTLY_AVAILABLE:
                    # Chart options
                    chart_type = st.selectbox("Pilih Jenis Grafik", ["Garis", "Batang", "Area"])
                    
                    # Prepare data for charts - group by day to show daily data points on x-axis
                    filtered_df['Tanggal_only'] = filtered_df['Tanggal'].dt.date
                    pemasukan = filtered_df[filtered_df["Jenis"] == "Pemasukan"].groupby("Tanggal_only")["Jumlah"].sum()
                    pengeluaran = filtered_df[filtered_df["Jenis"] == "Pengeluaran"].groupby("Tanggal_only")["Jumlah"].sum()
                    
                    # Create combined dataframe
                    chart_data = pd.DataFrame({
                        "Pemasukan": pemasukan,
                        "Pengeluaran": pengeluaran
                    }).fillna(0)
                    
                    # Create chart using Plotly for better date formatting
                    dates = chart_data.index
                    fig = go.Figure()
                    
                    if chart_type == "Garis":
                        fig.add_trace(go.Scatter(x=dates, y=chart_data["Pemasukan"], mode='lines+markers', name='Pemasukan', line=dict(color='#2ecc71')))
                        fig.add_trace(go.Scatter(x=dates, y=chart_data["Pengeluaran"], mode='lines+markers', name='Pengeluaran', line=dict(color='#e74c3c')))
                    elif chart_type == "Batang":
                        fig.add_trace(go.Bar(x=dates, y=chart_data["Pemasukan"], name='Pemasukan', marker_color='#2ecc71'))
                        fig.add_trace(go.Bar(x=dates, y=chart_data["Pengeluaran"], name='Pengeluaran', marker_color='#e74c3c'))
                    else:  # Area
                        fig.add_trace(go.Scatter(x=dates, y=chart_data["Pemasukan"], mode='lines', fill='tonexty', name='Pemasukan', line=dict(color='#2ecc71', width=0), fillcolor='rgba(46, 204, 113, 0.2)'))
                        fig.add_trace(go.Scatter(x=dates, y=chart_data["Pengeluaran"], mode='lines', fill='tonexty', name='Pengeluaran', line=dict(color='#e74c3c', width=0), fillcolor='rgba(231, 76, 60, 0.2)'))
                    
                    # Update layout with date formatting
                    fig.update_layout(
                        title="Analisis Pemasukan dan Pengeluaran",
                        xaxis_title="Tanggal",
                        yaxis_title="Jumlah (Rp)",
                        xaxis=dict(
                            tickformat="%d %B",  # Format: Day Month (e.g., 01 Januari)
                            dtick="D1",  # Show daily ticks
                        ),
                        hovermode='x unified',
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Modul plotly tidak tersedia. Menampilkan grafik menggunakan alternatif...")
                    
                    # Use Streamlit's built-in charting as fallback
                    # Prepare data for charts - group by day to show daily data points
                    filtered_df['Tanggal_only'] = filtered_df['Tanggal'].dt.date
                    chart_data = filtered_df.groupby(['Tanggal_only', 'Jenis'])['Jumlah'].sum().unstack(fill_value=0)
                    
                    # Rename columns to English for Streamlit compatibility
                    chart_data.columns = [col.replace('Pemasukan', 'Pemasukan').replace('Pengeluaran', 'Pengeluaran') for col in chart_data.columns]
                    
                    st.line_chart(chart_data)
                
                # Additional insights
                st.subheader("Insight")
                avg_pengeluaran = filtered_df[filtered_df['Jenis'] == 'Pengeluaran']['Jumlah'].mean()
                avg_pemasukan = filtered_df[filtered_df['Jenis'] == 'Pengeluaran']['Jumlah'].mean()
                
                if avg_pengeluaran > 0:
                    rasio = avg_pemasukan / avg_pengeluaran
                    if rasio > 1:
                        st.info(f"Rasio pemasukan terhadap pengeluaran: {rasio:.2f}x (baik, pemasukan lebih besar dari pengeluaran)")
                    else:
                        st.warning(f"Rasio pemasukan terhadap pengeluaran: {rasio:.2f}x (peringatan, pengeluaran lebih besar dari pemasukan)")
            else:
                st.warning("Tidak ada data dalam rentang tanggal yang dipilih.")

    elif menu == "AI Assistant":
        st.markdown('<h1 class="sub-header">🤖 AI Assistant Keuangan</h1>', unsafe_allow_html=True)
        df = get_transactions(st.session_state.email)
        if df.empty:
            st.info("Masukkan data terlebih dahulu untuk mendapatkan saran keuangan otomatis.")
        else:
            with st.spinner("AI sedang menganalisis keuangan Anda..."):
                advice = generate_financial_advice(df, st.session_state.kategori_pengguna)
            
            st.markdown(f'<div class="advice-box">{advice}</div>', unsafe_allow_html=True)

    elif menu == "Export Data":
        st.markdown('<h1 class="sub-header">📤 Export Laporan</h1>', unsafe_allow_html=True)
        df = get_transactions(st.session_state.email)
        if df.empty:
            st.info("Tidak ada data untuk diekspor.")
        else:
            # Summary information
            total_pemasukan = df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum()
            total_pengeluaran = df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
            saldo = total_pemasukan - total_pengeluaran
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Pemasukan", f"Rp{total_pemasukan:,.0f}")
            with col2:
                st.metric("Total Pengeluaran", f"Rp{total_pengeluaran:,.0f}")
            with col3:
                st.metric("Saldo", f"Rp{saldo:,.0f}")
            
            st.subheader("Pilih Format Ekspor")
            
            # Export options in columns
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download CSV",
                    data=export_to_csv(df),
                    file_name="laporan_keuangan.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col2:
                st.download_button(
                    label="📄 Download PDF",
                    data=export_to_pdf(df),
                    file_name="laporan_keuangan.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            # Show preview of data to be exported
            st.subheader("Pratinjau Data")
            st.dataframe(df, use_container_width=True)
