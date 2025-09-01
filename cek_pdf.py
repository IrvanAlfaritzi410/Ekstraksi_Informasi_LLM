# isi file cek_pdf.py (versi yang sudah diperbaiki)

import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import os

# --- DAFTAR URL YANG INGIN ANDA CEK ---
list_url_putusan = [
    "https://putusan3.mahkamahagung.go.id/direktori/putusan/42dfaa53298aa3a2649588946b89167e.html"
]
# -----------------------------------------------

# Looping untuk memproses setiap URL dalam daftar
for url in list_url_putusan:
    print(f"--- MEMPROSES URL: {url} ---")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'} # Menyamar sebagai browser
        pdf_content = None

        # Cek apakah link adalah halaman web atau link PDF langsung
        if url.lower().endswith('.pdf'):
            print("  └─ Link PDF langsung. Mengunduh...")
            pdf_url = url
        else:
            print("  └─ Link halaman web. Mencari link PDF...")
            page_response = requests.get(url, headers=headers, timeout=15)
            page_response.raise_for_status()
            
            soup = BeautifulSoup(page_response.content, 'html.parser')
            pdf_link_tag = soup.find('a', href=lambda href: href and "/pdf/" in href)
            
            if not pdf_link_tag:
                print("  └─ ✗ Gagal: Link unduhan PDF tidak ditemukan di halaman ini.\n")
                continue # Lanjut ke URL berikutnya
                
            pdf_url = pdf_link_tag['href']
            print(f"  └─ ✓ Link PDF ditemukan: {pdf_url}")

        # Unduh konten file PDF
        pdf_response = requests.get(pdf_url, headers=headers, timeout=30)
        pdf_response.raise_for_status()
        pdf_content = pdf_response.content
        
        # Buka PDF dari konten yang diunduh (di memori) dan ekstrak teksnya
        with fitz.open(stream=pdf_content, filetype="pdf") as doc:
            raw_text = "".join(page.get_text() for page in doc)

        # Tampilkan teks mentah
        print("\n--- ISI TEKS MENTAH ---")
        print(raw_text)
        print("-------------------------\n")

    except Exception as e:
        print(f"✗ Terjadi error saat memproses URL: {e}\n")

