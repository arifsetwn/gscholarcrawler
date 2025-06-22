# Google Scholar Publication Crawler

Script Python untuk crawling data publikasi dari Google Scholar berdasarkan ID user dan tahun publikasi.

## Instalasi

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Penggunaan

### Command Line
```bash
# Crawl semua publikasi dari scholar ID
python google_scholar_crawler.py CJMh47UAAAAJ

# Crawl publikasi tahun tertentu
python google_scholar_crawler.py CJMh47UAAAAJ --year 2022

# Custom output files
python google_scholar_crawler.py CJMh47UAAAAJ --year 2022 --output publications_2022.xlsx --wordcloud wordcloud_2022.png
```

### Parameter
- `scholar_id`: ID Google Scholar (wajib)
- `--year`: Tahun publikasi yang ingin difilter (opsional)
- `--output`: Nama file Excel output (default: output.xlsx)
- `--wordcloud`: Nama file word cloud output (default: wordcloud.png)

## Output

Script akan menghasilkan:
1. **File Excel** dengan kolom:
   - Judul
   - Nama Jurnal/Konferensi
   - Tahun
   - Penulis
   - Kutipan

2. **Word Cloud** dari kata kunci dalam judul publikasi

## Contoh Penggunaan

```bash
python google_scholar_crawler.py CJMh47UAAAAJ --year 2022
```

Script ini akan:
- Mengambil semua publikasi dari scholar ID `CJMh47UAAAAJ` tahun 2022
- Menyimpan data ke `output.xlsx`
- Membuat word cloud dan menyimpan ke `wordcloud.png`