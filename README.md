# 📊 Smart Buku Keuangan - Keuangan Pintar untuk Berbagai Kategori Pengguna

Smart Buku Keuangan adalah aplikasi pencatatan keuangan berbasis web menggunakan Streamlit yang dirancang untuk berbagai kategori pengguna: keluarga, pribadi, siswa, pedagang, UMKM, pengusaha, hingga pebisnis. Aplikasi ini membantu pengguna mengelola keuangan secara efektif dan memberikan saran keuangan yang relevan berdasarkan data yang dimasukkan.

## ✨ Fitur Utama

- ✅ **Input data keuangan** - Catat pemasukan, pengeluaran, tabungan, hutang, dan transaksi lainnya
- 📊 **Visualisasi data** - Grafik pemasukan vs pengeluaran yang interaktif
- 🤖 **AI Assistant** - Saran keuangan otomatis berbasis OpenAI
- 📤 **Export data** - Ekspor laporan ke format CSV dan PDF
- 📈 **Analisis keuangan** - Insight mendalam tentang pola keuangan Anda
- 👤 **Kategori pengguna** - Solusi keuangan yang disesuaikan dengan jenis pengguna

## 🛠️ Teknologi yang Digunakan

- **Python** - Bahasa pemrograman utama
- **Streamlit** - Framework untuk pembuatan aplikasi web interaktif
- **SQLite** - Database lokal untuk menyimpan transaksi
- **Pandas** - Pengolahan dan analisis data
- **FPDF** - Pembuatan laporan PDF
- **OpenAI** - Teknologi AI untuk saran keuangan
- **Matplotlib/Altair** - Visualisasi data (built-in Streamlit)

## 📋 Prasyarat

- Python 3.7 atau lebih tinggi
- Koneksi internet (untuk fitur AI)
- (Opsional) API Key OpenAI untuk fitur AI Assistant

## 🚀 Cara Menjalankan Aplikasi

### 1. Clone Repository
```bash
git clone <URL_REPOSITORY_INI>
cd Keuangan-Pintar
```

### 2. Buat Virtual Environment (Direkomendasikan)
```bash
python -m venv .venv
source .venv/bin/activate  # Di Linux/Mac
# atau
.venv\Scripts\activate     # Di Windows
```

### 3. Instal Dependencies
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi API Key OpenAI (Opsional)
Jika ingin menggunakan fitur AI Assistant, tambahkan API key OpenAI Anda pada environment variable:
```bash
export OPENAI_API_KEY="sk-your-openai-api-key-here"
```
Atau buat file `.env` di root project:
```
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 5. Jalankan Aplikasi
```bash
streamlit run app.py
```

Aplikasi akan berjalan di browser Anda di `http://localhost:8501`

## 📖 Cara Menggunakan Aplikasi

1. **Login**
   - Masukkan nama lengkap Anda
   - Isi alamat email
   - Pilih kategori pengguna (Keluarga, Pribadi, Siswa/Mahasiswa, Pedagang, UMKM, Pengusaha, Pebisnis)

2. **Input Data**
   - Pilih menu "Input Data" di sidebar
   - Masukkan tanggal transaksi
   - Pilih jenis transaksi (Pemasukan, Pengeluaran, Tabungan, Hutang, Lainnya)
   - Isi jumlah uang dan deskripsi
   - Tambahkan catatan tambahan jika perlu
   - Klik "Simpan Transaksi"

3. **Lihat dan Analisis Data**
   - Gunakan menu "Lihat Catatan" untuk melihat riwayat transaksi
   - Gunakan "Grafik & Insight" untuk visualisasi data keuangan
   - Filter data berdasarkan rentang tanggal

4. **Dapatkan Saran Keuangan**
   - Akses "AI Assistant" untuk mendapatkan saran keuangan otomatis
   - Sistem akan menganalisis transaksi Anda dan memberikan rekomendasi

5. **Export Data**
   - Gunakan menu "Export Data" untuk mengunduh laporan dalam format CSV atau PDF

## 🏗️ Struktur Proyek

```
Keuangan-Pintar/
├── app.py                 # File utama aplikasi Streamlit
├── requirements.txt      # Dependencies proyek
├── README.md            # Dokumentasi proyek
├── database/
│   └── keuangan.db      # Database lokal SQLite
└── utils/
    ├── helpers.py       # Fungsi bantuan untuk database
    ├── export.py        # Fungsi ekspor data
    └── ai.py            # Logika AI Assistant
```

## 📦 Dependencies

Semua dependencies tercantum dalam file `requirements.txt`. Instalasi otomatis dapat dilakukan dengan:
```bash
pip install -r requirements.txt
```

Daftar dependencies utama:
- streamlit
- pandas
- fpdf
- openai

## 🚀 Deployment

### 1. Deployment ke Streamlit Sharing
1. Fork repository ini di GitHub
2. Buka [Share Streamlit](https://share.streamlit.io/)
3. Tambahkan repository Anda
4. Atur path ke `app.py`
5. Tambahkan environment variable untuk `OPENAI_API_KEY` jika menggunakan fitur AI

### 2. Deployment ke Heroku
1. Pastikan Anda memiliki akun Heroku dan Heroku CLI terinstal
2. Buat aplikasi baru di Heroku
3. Tambahkan buildpack Python
4. Deploy repository menggunakan Git

### 3. Deployment ke VPS
1. Clone repository di server
2. Instal dependencies
3. Konfigurasi reverse proxy (misalnya Nginx)
4. Gunakan PM2 atau systemd untuk menjaga aplikasi berjalan

### Contoh Konfigurasi untuk Production
```bash
# Untuk deployment production, Anda bisa menggunakan:
streamlit run app.py --server.port 80 --server.headless true
```

## 🔐 Konfigurasi Security untuk Production

- Gunakan HTTPS
- Jangan hardcode API key dalam kode
- Gunakan environment variables
- Batasi akses IP jika diperlukan
- Backup database secara rutin

## 🤖 Fitur AI Assistant

Aplikasi dilengkapi dengan AI Assistant yang memberikan saran keuangan berdasarkan data transaksi pengguna. Fitur ini menggunakan OpenAI GPT-3.5-turbo untuk:
- Menganalisis pola pengeluaran dan pemasukan
- Memberikan saran keuangan personalisasi
- Menyarankan strategi penghematan dan investasi

Untuk menggunakan fitur ini, pastikan Anda memiliki OpenAI API key yang valid.

## 📊 Kategori Pengguna

Aplikasi dirancang untuk berbagai kategori pengguna:
- **Keluarga** - Manajemen keuangan rumah tangga
- **Pribadi** - Catatan keuangan individu
- **Siswa/Mahasiswa** - Pengelolaan uang saku
- **Pedagang** - Catatan transaksi dagang
- **UMKM** - Pembukuan usaha kecil
- **Pengusaha** - Manajemen keuangan bisnis
- **Pebisnis** - Analisis keuangan skala besar

## 🙏 Kontribusi

Kami menyambut kontribusi dari komunitas! Jika Anda ingin berkontribusi:

1. Fork repository ini
2. Buat branch fitur (`git checkout -b fitur-hebat`)
3. Commit perubahan Anda (`git commit -m 'Tambah fitur hebat'`)
4. Push ke branch (`git push origin fitur-hebat`)
5. Buka Pull Request

## 📄 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).

## 🆘 Dukungan

Jika Anda mengalami masalah atau memiliki pertanyaan, silakan:
- Buka issue di repository GitHub
- Hubungi pengembang langsung
- Periksa dokumentasi tambahan jika tersedia
