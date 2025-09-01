# extractor.py

import google.generativeai as genai
import json
import textwrap

# PROMPT UNIVERSAL DENGAN CONTOH FEW-SHOT
# Instruksi dasar untuk model
PROMPT_UNIVERSAL = """
Anda adalah asisten hukum AI yang sangat ahli dalam menganalisis dan menstrukturkan dokumen putusan pengadilan di Indonesia.
Tugas Anda adalah membaca teks putusan dan mengekstrak semua informasi yang relevan ke dalam format JSON.

INSTRUKSI PENTING:
1.  **Format JSON**: Selalu kembalikan satu objek JSON yang valid.
2.  **Para Pihak**: `para_pihak` adalah array objek, ekstrak SEMUA pihak yang terlibat.
3.  **Rangkuman**: Buat rangkuman singkat untuk semua field deskriptif.
4.  **Nilai Null**: Jika informasi tidak ditemukan, WAJIB gunakan nilai `null`.
5.  **Tanggal**: Gunakan format `YYYY-MM-DD`.
6.  **Nomor Identitas**: Ekstrak HANYA angka untuk nomor identitas.

Berikut adalah beberapa contoh ekstraksi yang benar (Teks -> JSON) untuk memandu Anda.

---
"""

# Contoh JSON yang Anda berikan, disimpan sebagai objek Python.
# Ini akan digunakan untuk membuat prompt few-shot secara dinamis.
EXAMPLE_JSON_LIST = [
    # ... (contoh JSON yang sudah Anda berikan)
    {
        "klasifikasi_perkara": "Pidana Umum",
        "informasi_umum": {
            "nomor_putusan": "207/Pid.B/2018/PN Jmr",
            "nama_pengadilan": "Pengadilan Negeri Jember",
            "tingkat_pengadilan": "Pengadilan Negeri",
            "tanggal_putusan": "2018-05-08"
        },
        "para_pihak": [
            {
                "peran_pihak": "Terdakwa",
                "nama_lengkap": "Eko Setyawan",
                "tempat_lahir": "Jember",
                "tanggal_lahir": "1974-08-11",
                "usia": 43,
                "jenis_kelamin": "Laki-laki",
                "pekerjaan": "Wiraswasta",
                "agama": "Islam",
                "alamat": "Jl. Citra Pahlawan Dusun Krajan II RT.002 RW.007 Desa Keting Kecamatan Jombang Kabupaten Jember",
                "NIK": None,
                "nomor_kk": None,
                "nomor_akta_kelahiran": None,
                "nomor_paspor": None
            }
        ],
        "detail_perkara": {
            "riwayat_perkara": "Terdakwa Eko Setyawan didakwa melakukan tindak pidana mencetak, menerbitkan, dan mendistribusikan dokumen kependudukan (e-KTP) palsu...",
            "dakwaan_jpu": "Jaksa Penuntut Umum mendakwa Terdakwa Eko Setyawan secara alternatif...",
            "pokok_gugatan": None,
            "riwayat_penahanan": "Terdakwa Eko Setyawan ditahan Rutan secara bertahap oleh Penyidik, Penuntut Umum, dan Hakim Pengadilan Negeri..."
        },
        "amar_putusan": {
            "amar_putusan_jpu": "Menyatakan Terdakwa EKO SETYAWAN bersalah melakukan tindak pidana tanpa hak mencetak, menerbitkan, dan/atau mendistribusikan dokumen kependudukan...",
            "amar_putusan_pn_pa_ptun": "Menyatakan terdakwa EKO SETYAWAN bersalah melakukan tindak pidana tanpa hak mencetak...",
            "amar_putusan_pt_pta_pttun": None,
            "amar_putusan_kasasi": None
        },
        "analisis_hukum": {
            "pertimbangan_hukum": "Majelis Hakim menyatakan Terdakwa terbukti secara sah dan meyakinkan memenuhi unsur 'Setiap orang' dan 'yang tanpa hak mencetak...'...",
            "formalitas_permohonan": None
        }
    }
]

def ekstrak_data_dengan_langextract(teks_list, model_id):
    """
    Menganalisis teks dari daftar chunks menggunakan LangExtract dan model Gemini.
    """
    results = []
    
    # Mengonfigurasi prompt few-shot
    prompt_with_examples = PROMPT_UNIVERSAL
    for example in EXAMPLE_JSON_LIST:
        json_string = json.dumps(example, indent=4, ensure_ascii=False)
        prompt_with_examples += f"""
Input Teks:
(Teks putusan lengkap dari contoh)

Output JSON:
\"\"\"
{json_string}
\"\"\"

---
"""
    
    # Memproses setiap chunk teks dari PDF
    for teks_chunk in teks_list:
        try:
            prompt_final = prompt_with_examples + f"""
Input Teks:
\"\"\"
{teks_chunk}
\"\"\"

Output JSON:
\"\"\"
"""
            response = genai.GenerativeModel(model_id).generate_content(
                prompt_final,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                )
            )
            results.append(json.loads(response.text))
        except Exception as e:
            print(f"  └─ ✗ Error saat memproses chunk dengan Gemini: {e}")
            results.append(None)
            
    return results

