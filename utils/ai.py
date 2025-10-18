import os
import pandas as pd

def generate_financial_advice(df, kategori_pengguna):
    pemasukan_total = df[df['Jenis'] == 'Pemasukan']['Jumlah'].sum()
    pengeluaran_total = df[df['Jenis'] == 'Pengeluaran']['Jumlah'].sum()
    tabungan_total = df[df['Jenis'] == 'Tabungan']['Jumlah'].sum()

    # Check if we have OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if openai_api_key and openai_api_key != "your-openai-api-key":
        import openai
        openai.api_key = openai_api_key

        try:
            prompt = f"""
Saya adalah pengguna kategori: {kategori_pengguna}.
Berikut adalah data keuangan saya bulan ini:
- Total pemasukan: Rp{pemasukan_total:,.0f}
- Total pengeluaran: Rp{pengeluaran_total:,.0f}
- Total tabungan: Rp{tabungan_total:,.0f}

Berikan saya saran keuangan singkat dalam 2-3 poin yang relevan dengan kondisi ini.
"""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7,
            )
            advice = response['choices'][0]['message']['content'].strip()
        except Exception as e:
            advice = f"Gagal mendapatkan saran AI. Silakan cek koneksi atau API key Anda. Error: {str(e)}"
    else:
        # Provide basic financial advice without AI
        balance = pemasukan_total - pengeluaran_total
        if balance > 0:
            advice = f"""
Saran Keuangan Otomatis:
1. Anda memiliki surplus keuangan sebesar Rp{balance:,.0f}. Pertimbangkan untuk menambah tabungan atau investasi.
2. Kategorikan pengeluaran Anda untuk pengelolaan yang lebih baik ({kategori_pengguna}).
3. Buat anggaran bulanan untuk menjaga keseimbangan keuangan.
            """.strip()
        elif balance < 0:
            advice = f"""
Saran Keuangan Otomatis:
1. Anda mengalami defisit sebesar Rp{abs(balance):,.0f}. Coba evaluasi pengeluaran yang bisa dikurangi ({kategori_pengguna}).
2. Prioritaskan pengeluaran penting dan hindari pengeluaran non-esensial.
3. Cari sumber pemasukan tambahan untuk menyeimbangkan keuangan Anda.
            """.strip()
        else:
            advice = f"""
Saran Keuangan Otomatis:
1. Keuangan Anda saat ini seimbang. Pertahankan pengelolaan yang baik ({kategori_pengguna}).
2. Tetap awasi pemasukan dan pengeluaran secara berkala.
3. Mulailah menabung untuk masa depan yang lebih baik.
            """.strip()

    return advice
