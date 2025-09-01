# config.py
# Berisi semua variabel konfigurasi proyek.

import os
from dotenv import load_dotenv

# Memuat variabel dari file .env
load_dotenv()

# --- Konfigurasi Gemini ---
MODEL_NAME = 'gemini-1.5-flash-latest'
GOOGLE_API_KEY = os.getenv('GEMINI_API_KEY')

# --- Konfigurasi MinIO ---
# PERBAIKAN: Menggunakan host.docker.internal untuk koneksi dari Docker ke host
MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT', 'localhost:9000')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')

# --- Konfigurasi Output ---
PDF_DOWNLOAD_FOLDER = 'downloaded_pdfs'
OUTPUT_FILENAME_JSONL = 'hasil_ekstraksi_putusan.jsonl'
OUTPUT_FILENAME_HTML = 'visualisasi_ekstraksi.html'
