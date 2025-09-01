import os
import json
import textwrap
import webbrowser

def create_simple_html_visualization(data_list):
    """
    Creates a simple HTML visualization from a list of document data.
    This function generates the full HTML content as a single string.
    """
    # Escape special characters for safe HTML display
    def escape_html(text):
        if text is None:
            return ''
        return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Visualisasi Hasil Ekstraksi Putusan</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 3px solid #2c3e50; }
        .header h1 { color: #2c3e50; margin: 0; font-size: 2.5em; }
        .stats { background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 30px; font-size: 1.2em; }
        .document { border: 1px solid #ddd; margin: 20px 0; padding: 25px; border-radius: 8px; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .document:hover { box-shadow: 0 3px 8px rgba(0,0,0,0.15); transition: box-shadow 0.3s ease; }
        .metadata { background-color: #ecf0f1; padding: 15px; margin-bottom: 20px; border-radius: 5px; border-left: 4px solid #3498db; }
        .text-content { line-height: 1.8; font-size: 1.1em; white-space: pre-wrap; }
        .json-content { background-color: #2b2b2b; color: #f8f8f2; padding: 10px; border-radius: 5px; font-family: 'Courier New', Courier, monospace; overflow-x: auto; }
        h2 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-top: 0; }
        h3 { color: #34495e; margin-top: 0; }
        ul { list-style-type: none; padding: 0; }
        li { padding: 8px 0; border-bottom: 1px solid #ecf0f1; }
        li:last-child { border-bottom: none; }
        .key { font-weight: bold; color: #2c3e50; display: inline-block; min-width: 150px; }
        .value { color: #34495e; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 Hasil Ekstraksi Putusan Hukum</h1>
        </div>
        <div class="stats">
            Total Dokumen Berhasil Diekstrak: <strong>%s</strong>
        </div>
""" % len(data_list)

    for i, data in enumerate(data_list):
        html += f"""
        <div class="document">
            <h2>📄 Dokumen {i+1}</h2>
            <div class="metadata">
                <h3>ℹ️ Informasi Metadata:</h3>
                <ul>
        """
        
        # Tampilkan metadata dengan formatting lebih baik
        for key, value in data.items():
            if key not in ['teks_asli', 'annotations', 'ekstraksi_json']:
                formatted_key = key.replace('_', ' ').title()
                html += f'<li><span class="key">{formatted_key}:</span> <span class="value">{escape_html(value)}</span></li>\n'
        
        html += f"""
                </ul>
            </div>
            <div class="text-content">
                <h3>📝 Teks Putusan Asli:</h3>
                <pre>{escape_html(data.get('teks_asli', 'Tidak ada teks tersedia'))}</pre>
            </div>
            <div class="json-content">
                <h3>💻 Hasil Ekstraksi JSON:</h3>
                <pre>{json.dumps(data.get('ekstraksi_json', {}), indent=2, ensure_ascii=False)}</pre>
            </div>
        </div>
        """
    
    html += """
    </div>
</body>
</html>
"""
    return html

def main():
    jsonl_file = 'hasil_ekstraksi_putusan.jsonl'
    html_file = 'visualisasi_ekstraksi.html'
    
    if not os.path.exists(jsonl_file):
        print(f"✗ File '{jsonl_file}' tidak ditemukan. Silakan jalankan main.py untuk membuatnya.")
        return
        
    print(f"✓ Membaca data dari '{jsonl_file}'...")
    data_list = []
    try:
        with open(jsonl_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.strip():
                    data_list.append(json.loads(line))
        
        if data_list:
            print("✓ Data berhasil dimuat. Membuat visualisasi HTML...")
            html_content = create_simple_html_visualization(data_list)
            
            with open(html_file, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(html_content)
                
            print(f"✓ Visualisasi HTML berhasil dibuat di '{html_file}'")
            print("Anda bisa buka file ini di browser Anda.")
            webbrowser.open(f'file://{os.path.abspath(html_file)}')
        else:
            print("✗ File JSONL kosong atau tidak valid.")
            
    except Exception as e:
        print(f"✗ Terjadi error saat membuat visualisasi: {e}")

if __name__ == "__main__":
    main()
