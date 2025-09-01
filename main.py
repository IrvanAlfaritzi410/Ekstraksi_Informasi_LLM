import os
import json
import time
import webbrowser
import boto3
import textwrap
from botocore.client import Config
import langextract as lx
import google.generativeai as genai
from proses_URL import proses_putusan_from_url
import config
from visualizer import create_simple_html_visualization

# --- MENGKONFIGURASI GEMINI API SEKALI SAJA DI AWAL ---
def setup_model():
    """Mengkonfigurasi dan mengembalikan model Gemini menggunakan variabel dari config."""
    if config.GOOGLE_API_KEY:
        try:
            genai.configure(api_key=config.GOOGLE_API_KEY)
            model = genai.GenerativeModel(config.MODEL_NAME)
            print("✓ Konfigurasi Gemini API berhasil.")
            return model
        except Exception as e:
            print(f"✗ Konfigurasi API gagal: {e}")
            return None
    else:
        print("✗ Kunci API tidak tersedia di config.py atau .env file.")
        return None

def setup_s3_client():
    print("✓ Menyiapkan koneksi ke MinIO...")
    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=f'http://{config.MINIO_ENDPOINT}',
            aws_access_key_id=config.MINIO_ACCESS_KEY,
            aws_secret_access_key=config.MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4')
        )
        print("✓ Koneksi MinIO berhasil.")
        return s3_client
    except Exception as e:
        print(f"✗ Koneksi MinIO gagal: {e}")
        return None

def main():
    # PANGGIL setup_model() di sini untuk memastikan API terkonfigurasi
    model = setup_model()
    s3_client = setup_s3_client()
    
    if not model or not s3_client:
        print("Eksekusi dihentikan karena konfigurasi gagal.")
        return
    
    list_url_putusan = [
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/42dfaa53298aa3a2649588946b89167e.html",
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/zaf066d7f7faca26a8ec313534333431.html",
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/84771ffa631520272cab7efbc09042c0.html",
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/zaf067e157fcc1909741323332333138.html",
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/zaf067e2e205590ab675323335343230.html",
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/zaf067e585702cbcb020323335333133.html",
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/zaf067e62ebdd8289d9d323335373537.html",
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/zaec3dd5a5b1913e9c3e303831333535.html",
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/e88eb8fdfa67097f9e12cfd7a761f95e.html",
        "https://putusan3.mahkamahagung.go.id/direktori/putusan/7adebc7fee0522e2d3a08718a62f9d0c.html"
    ]
    
    list_hasil_akhir = []
    if os.path.exists(config.OUTPUT_FILENAME_JSONL):
        try:
            with open(config.OUTPUT_FILENAME_JSONL, 'r', encoding='utf-8', errors='ignore') as f:
                list_hasil_akhir = [json.loads(line) for line in f]
        except json.JSONDecodeError:
            list_hasil_akhir = []
            print(f"✗ Peringatan: File '{config.OUTPUT_FILENAME_JSONL}' rusak. Memulai dari awal.")
    
    processed_urls = {item.get('sumber_url') for item in list_hasil_akhir}
    urls_to_process = [url for url in list_url_putusan if url not in processed_urls]

    if not urls_to_process:
        print("\n✓ Semua URL sudah diproses sebelumnya.")
    else:
        print(f"\nMenemukan {len(urls_to_process)} URL baru untuk diproses.")
        for i, url in enumerate(urls_to_process):
            hasil = proses_putusan_from_url(model, s3_client, url)
            if hasil:
                list_hasil_akhir.append(hasil)
                print("  └─ ✓ Ekstraksi dari URL berhasil!\n")
            else:
                print("  └─ ✗ Gagal memproses URL ini.\n")
            
            if i < len(urls_to_process) - 1:
                print(f"  └─ Menunggu 15 detik sebelum memproses URL berikutnya...")
                time.sleep(15)

    if list_hasil_akhir:
        print(f"\nMenyimpan total {len(list_hasil_akhir)} data ke dalam file JSONL...")
        with open(config.OUTPUT_FILENAME_JSONL, 'w', encoding='utf-8', errors='ignore') as f:
            for item in list_hasil_akhir:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"✓ Data berhasil disimpan di '{config.OUTPUT_FILENAME_JSONL}'")
        
        print(f"\nMembuat visualisasi HTML...")
        try:
            html_content = create_simple_html_visualization(list_hasil_akhir)
            with open(config.OUTPUT_FILENAME_HTML, "w", encoding='utf-8') as f:
                f.write(html_content)
            print(f"✓ Visualisasi HTML sederhana berhasil dibuat di '{config.OUTPUT_FILENAME_HTML}'")
        except Exception as e:
            print(f"✗ Gagal membuat visualisasi HTML: {e}")
            
        
        if os.path.exists(config.OUTPUT_FILENAME_HTML):
            html_path = os.path.abspath(config.OUTPUT_FILENAME_HTML)
            print(f"🌐 Membuka visualisasi di browser: {html_path}")
            try:
                webbrowser.open(f'file://{html_path}')
                print("✓ Visualisasi berhasil dibuka di browser default")
            except Exception as e:
                print(f"✗ Gagal membuka browser otomatis: {e}")
                print(f"    Anda bisa buka manual: file://{html_path}")
    else:
        print("\nTidak ada data yang berhasil diekstrak.")

if __name__ == "__main__":
    main()
