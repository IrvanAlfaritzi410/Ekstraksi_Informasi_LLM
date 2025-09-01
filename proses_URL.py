# proses_URL.py

# --- Library Pihak Ketiga ---
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import io
import time
import json
import re
import google.generativeai as genai

# --- Library Standar Python ---
import os

# --- Impor dari Modul Proyek Lain ---
from extractor import ekstrak_data_dengan_langextract
import config

def bersihkan_teks_pdf(doc):
    """
    Mengekstrak dan membersihkan teks dari objek PDF, halaman per halaman.
    """
    cleaned_text_per_page = []
    # Memproses setiap halaman PDF secara terpisah
    for page in doc:
        page_text = page.get_text()
        # Membersihkan teks dari karakter yang tidak diinginkan dan spasi berlebih
        # PERBAIKAN: Mengganti spasi non-standar dan karakter yang tidak valid
        cleaned_text = re.sub(r'[\s\x00-\x1F\x7F-\xFF]+', ' ', page_text).strip()
        cleaned_text_per_page.append(cleaned_text)
    
    # Menggabungkan semua teks yang sudah bersih menjadi satu string
    return " ".join(cleaned_text_per_page)

def pecah_teks_menjadi_chunks(teks, ukuran_chunk=8000):
    """
    Memecah teks panjang menjadi daftar chunks yang lebih kecil.
    """
    chunks = []
    current_pos = 0
    while current_pos < len(teks):
        chunks.append(teks[current_pos:current_pos+ukuran_chunk])
        current_pos += ukuran_chunk
    return chunks

def proses_putusan_from_url(model, s3_client, url):
    print(f"Memproses URL: {url}")
    
    MAX_RETRIES = 5
    retry_delay = 20

    for attempt in range(MAX_RETRIES):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            pdf_content = None
            pdf_filename = ""
            TIMEOUT = 60

            if url.lower().endswith('.pdf'):
                print("  └─ Terdeteksi link PDF langsung. Mengunduh file...")
                pdf_url = url
            else:
                print("  └─ Terdeteksi link halaman web. Mencari link PDF...")
                page_response = requests.get(url, headers=headers, timeout=TIMEOUT)
                page_response.raise_for_status()
                soup = BeautifulSoup(page_response.content, 'html.parser')
                pdf_link_tag = soup.find('a', href=lambda href: href and "/pdf/" in href)
                if not pdf_link_tag:
                    print("  └─ ✗ Link unduhan PDF tidak ditemukan.")
                    return None
                pdf_url = pdf_link_tag['href']
                print(f"  └─ ✓ Link PDF ditemukan: {pdf_url}")

            pdf_response = requests.get(pdf_url, headers=headers, timeout=TIMEOUT)
            pdf_response.raise_for_status() 
            pdf_content = pdf_response.content
            print("  └─ ✓ Konten PDF berhasil diunduh ke memori.")
            pdf_filename = pdf_url.split('/')[-1]
            if not pdf_filename.lower().endswith('.pdf'):
                pdf_filename += ".pdf"
            print(f"  └─ Mengunggah '{pdf_filename}' ke bucket MinIO '{config.MINIO_BUCKET_NAME}'...")
            s3_client.put_object(
                Bucket=config.MINIO_BUCKET_NAME,
                Key=pdf_filename,
                Body=pdf_content,
                ContentLength=len(pdf_content),
                ContentType='application/pdf'
            )
            print("  └─ ✓ PDF berhasil diunggah ke MinIO.")
            
            with fitz.open(stream=io.BytesIO(pdf_content), filetype="pdf") as doc:
                # Menggunakan fungsi pembersihan yang diperbaiki
                full_text = bersihkan_teks_pdf(doc)
            if not full_text.strip():
                print("  └─ ✗ Gagal mengekstrak teks dari PDF.")
                return None
            
            teks_chunks = pecah_teks_menjadi_chunks(full_text)
            print(f"  └─ Teks PDF dipecah menjadi {len(teks_chunks)} bagian.")
            
            print("  └─ Mengirim teks ke Gemini untuk ekstraksi...")
            hasil_json_list = ekstrak_data_dengan_langextract(teks_chunks, model_id=config.MODEL_NAME)
            
            if hasil_json_list:
                final_hasil_json = hasil_json_list[0]
                final_hasil_json['sumber_url'] = url
                final_hasil_json['nama_file_lokal'] = pdf_filename
                
                # PERBAIKAN: Menggunakan teks yang sudah bersih
                final_hasil_json['teks_asli'] = full_text
                
                return final_hasil_json
            
            print("  └─ ✗ Ekstraksi dari Gemini gagal. Mencoba lagi...")
            time.sleep(retry_delay)
            retry_delay *= 2
            
        except requests.exceptions.RequestException as e:
            print(f"  └─ ✗ Kesalahan jaringan: {e}. Mencoba lagi dalam {retry_delay} detik...")
            time.sleep(retry_delay)
            retry_delay *= 2
        
        except Exception as e:
            error_message = str(e)
            if "RESOURCE_EXHAUSTED" in error_message:
                print(f"  └─ ✗ Kuota API terlampaui. Mencoba lagi dalam {retry_delay} detik...")
                time.sleep(retry_delay)
                retry_delay *= 2
                continue
            else:
                print(f"  └─ ✗ Terjadi error: {error_message}")
                return None
    
    print(f"  └─ ✗ Gagal memproses URL setelah {MAX_RETRIES} percobaan.")
    return None
