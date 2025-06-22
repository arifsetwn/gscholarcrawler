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
  # Rentang tahun 2020-2023
  python google_scholar_crawler.py SCHOLAR_ID
  --start-year 2020 --end-year 2023

  # Mulai dari tahun 2020
  python google_scholar_crawler.py SCHOLAR_ID
  --start-year 2020

  # Sampai tahun 2023
  python google_scholar_crawler.py SCHOLAR_ID
  --end-year 2023

  # Tahun tunggal (cara lama tetap work)
  python google_scholar_crawler.py l1JmHE8AAAAJ --year 2025
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