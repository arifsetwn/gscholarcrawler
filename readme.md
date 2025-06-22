# Google Scholar Crawler

Aplikasi ini digunakan untuk mengambil (crawling) data publikasi dari akun Google Scholar berdasarkan ID user dan tahun publikasi tertentu. Data hasil crawling akan disimpan dalam file Excel dan divisualisasikan dalam bentuk word cloud dari judul publikasi.

## Fitur
- Mengambil data publikasi berdasarkan ID Google Scholar dan tahun publikasi.
- Menyimpan metadata publikasi ke file Excel (`output.xlsx`).
- Membuat dan menyimpan word cloud dari judul publikasi (`wordcloud.png`).
- Filtering otomatis berdasarkan tahun yang diinputkan (tunggal atau rentang tahun).

## Cara Instalasi

1. **Clone repository atau salin file script ke folder lokal Anda.**
2. **Install dependencies berikut di terminal:**
    ```bash
    pip install -r requirements.txt
    ```

## Cara Penggunaan

### Contoh Penggunaan di Terminal

```bash
# Rentang tahun 2020-2023
python google_scholar_crawler.py SCHOLAR_ID --start-year 2020 --end-year 2023

# Mulai dari tahun 2020
python google_scholar_crawler.py SCHOLAR_ID --start-year 2020

# Sampai tahun 2023
python google_scholar_crawler.py SCHOLAR_ID --end-year 2023

# Tahun tunggal (cara lama tetap work)
python google_scholar_crawler.py l1JmHE8AAAAJ --year 2025
```

Gantilah `SCHOLAR_ID` dengan ID Google Scholar yang ingin Anda crawl.

## Output

- **output.xlsx**  
  Berisi data publikasi pada tahun yang dipilih, dengan kolom:
  - Judul
  - Nama Jurnal / Konferensi
  - Tahun
  - Penulis
  - Kutipan

- **wordcloud.png**  
  Visualisasi word cloud dari kata kunci judul publikasi tahun tersebut.

## Catatan

- Pastikan ID Google Scholar valid dan publikasi pada tahun yang diminta tersedia.
- Jika tidak ada publikasi pada tahun tersebut, file output tidak akan dibuat.
- Script ini hanya mengambil data publikasi yang