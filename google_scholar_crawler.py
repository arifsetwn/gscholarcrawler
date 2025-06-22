#!/usr/bin/env python3
"""
Google Scholar Publication Crawler
Script untuk crawling data publikasi dari Google Scholar berdasarkan ID user dan tahun publikasi
"""

import pandas as pd
from scholarly import scholarly
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from collections import Counter
import argparse
import sys
import time
import urllib.parse
import nltk
from nltk.corpus import stopwords

def download_nltk_data():
    """
    Download NLTK data yang diperlukan jika belum ada
    """
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        print("Downloading NLTK stopwords data...")
        nltk.download('stopwords', quiet=True)

def get_stopwords():
    """
    Mendapatkan stopwords untuk bahasa Indonesia dan Inggris dengan tambahan akademik
    
    Returns:
        set: Set stopwords yang sudah digabung
    """
    download_nltk_data()
    
    # Stopwords bahasa Indonesia dan Inggris dari NLTK
    try:
        indonesian_stopwords = set(stopwords.words('indonesian'))
    except:
        indonesian_stopwords = set()
    
    try:
        english_stopwords = set(stopwords.words('english'))
    except:
        english_stopwords = set()
    
    # Custom academic and technical stopwords
    academic_stopwords = {
        # Academic terms (English)
        'using', 'based', 'approach', 'study', 'analysis', 'method', 'methods',
        'research', 'paper', 'article', 'journal', 'conference', 'proceedings',
        'international', 'national', 'annual', 'ieee', 'acm', 'springer',
        'publication', 'published', 'publisher', 'vol', 'volume', 'issue',
        'page', 'pages', 'pp', 'isbn', 'issn', 'doi', 'abstract', 'keywords',
        'introduction', 'conclusion', 'discussion', 'results', 'methodology',
        'literature', 'review', 'survey', 'overview', 'summary', 'case',
        'cases', 'example', 'examples', 'sample', 'samples', 'test', 'tests',
        'testing', 'evaluation', 'experiment', 'experiments', 'experimental',
        'empirical', 'theoretical', 'practical', 'application', 'applications',
        'implementation', 'development', 'design', 'framework', 'model',
        'models', 'modeling', 'modelling', 'algorithm', 'algorithms',
        'technique', 'techniques', 'technology', 'technologies', 'system',
        'systems', 'platform', 'platforms', 'tool', 'tools', 'software',
        'hardware', 'computer', 'computing', 'digital', 'electronic',
        'automatic', 'automated', 'manual', 'performance', 'efficiency',
        'effectiveness', 'optimization', 'optimal', 'solution', 'solutions',
        'problem', 'problems', 'issue', 'issues', 'challenge', 'challenges',
        
        # Academic terms (Indonesian)
        'penelitian', 'studi', 'analisis', 'metode', 'pendekatan', 'kajian',
        'jurnal', 'konferensi', 'prosiding', 'internasional', 'nasional',
        'publikasi', 'artikel', 'makalah', 'abstrak', 'kata', 'kunci',
        'pengantar', 'pendahuluan', 'kesimpulan', 'diskusi', 'hasil',
        'metodologi', 'literatur', 'tinjauan', 'survei', 'ringkasan',
        'contoh', 'sampel', 'uji', 'pengujian', 'evaluasi', 'eksperimen',
        'empiris', 'teoritis', 'praktis', 'aplikasi', 'implementasi',
        'pengembangan', 'desain', 'kerangka', 'model', 'algoritma',
        'teknik', 'teknologi', 'sistem', 'platform', 'alat', 'perangkat',
        'lunak', 'keras', 'komputer', 'komputasi', 'digital', 'elektronik',
        'otomatis', 'manual', 'kinerja', 'efisiensi', 'efektivitas',
        'optimasi', 'optimal', 'solusi', 'masalah', 'isu', 'tantangan',
        
        # Common words that should be filtered
        'data', 'dataset', 'datasets', 'database', 'databases', 'information',
        'knowledge', 'content', 'structure', 'function', 'functions', 'process',
        'processes', 'procedure', 'procedures', 'step', 'steps', 'stage',
        'stages', 'phase', 'phases', 'level', 'levels', 'type', 'types',
        'kind', 'kinds', 'form', 'forms', 'way', 'ways', 'manner', 'means',
        'end', 'ends', 'goal', 'goals', 'objective', 'objectives', 'purpose',
        'purposes', 'aim', 'aims', 'target', 'targets', 'focus', 'scope',
        'range', 'field', 'fields', 'area', 'areas', 'domain', 'domains'
    }
    
    # Gabungkan semua stopwords
    all_stopwords = indonesian_stopwords.union(english_stopwords).union(academic_stopwords)
    
    return all_stopwords

def get_author_publications(scholar_id, start_year=None, end_year=None):
    """
    Mengambil data publikasi dari Google Scholar berdasarkan ID author
    
    Args:
        scholar_id (str): ID Google Scholar author
        start_year (int): Tahun awal publikasi yang ingin difilter (opsional)
        end_year (int): Tahun akhir publikasi yang ingin difilter (opsional)
    
    Returns:
        list: Daftar publikasi yang sudah difilter
    """
    try:
        print(f"Mengambil data author dengan ID: {scholar_id}")
        
        # Ambil informasi author
        search_query = scholarly.search_author_id(scholar_id)
        author = scholarly.fill(search_query, sections=['publications'])
        
        author_name = author.get('name', 'Unknown')
        print(f"Author ditemukan: {author_name}")
        print(f"Total publikasi: {len(author.get('publications', []))}")
        
        publications = []
        
        for i, pub in enumerate(author.get('publications', [])):
            try:
                # Ambil detail lengkap publikasi
                pub_detail = scholarly.fill(pub)
                
                # Ekstrak tahun publikasi
                pub_year = None
                if 'pub_year' in pub_detail:
                    pub_year = int(pub_detail['pub_year'])
                elif 'bib' in pub_detail and 'pub_year' in pub_detail['bib']:
                    pub_year = int(pub_detail['bib']['pub_year'])
                
                # Filter berdasarkan rentang tahun jika ditentukan
                if start_year and pub_year and pub_year < start_year:
                    continue
                if end_year and pub_year and pub_year > end_year:
                    continue
                
                # Ekstrak venue dengan multiple fallbacks
                venue = 'Unknown'
                bib_data = pub_detail.get('bib', {})
                
                # Coba berbagai field untuk venue
                venue_fields = ['venue', 'journal', 'booktitle', 'conference', 'publisher']
                for field in venue_fields:
                    if bib_data.get(field) and bib_data[field].strip():
                        venue = bib_data[field].strip()
                        break
                
                # Jika masih Unknown, coba dari citation atau URL
                if venue == 'Unknown':
                    # Coba extract dari pub_url jika ada
                    pub_url = pub_detail.get('pub_url', '')
                    if pub_url:
                        # Extract dari domain atau path URL
                        parsed_url = urllib.parse.urlparse(pub_url)
                        netloc = parsed_url.netloc.lower()
                        if 'arxiv' in netloc:
                            venue = 'arXiv'
                        elif 'researchgate' in netloc:
                            venue = 'ResearchGate'
                        elif 'ieee' in netloc:
                            venue = 'IEEE'
                        elif 'acm' in netloc:
                            venue = 'ACM'
                        elif 'springer' in netloc:
                            venue = 'Springer'
                        elif 'elsevier' in netloc:
                            venue = 'Elsevier'
                        elif 'sciencedirect' in netloc:
                            venue = 'ScienceDirect'
                        elif 'wiley' in netloc:
                            venue = 'Wiley'
                        elif 'nature' in netloc:
                            venue = 'Nature'
                        elif 'science' in netloc:
                            venue = 'Science'
                        elif 'plos' in netloc:
                            venue = 'PLOS'
                        elif 'mdpi' in netloc:
                            venue = 'MDPI'
                        elif 'frontiers' in netloc:
                            venue = 'Frontiers'
                    
                    # Coba extract dari eprint_url atau scholar_url
                    if venue == 'Unknown':
                        eprint_url = pub_detail.get('eprint_url', '')
                        if eprint_url and 'arxiv' in eprint_url.lower():
                            venue = 'arXiv'
                
                # Clean venue name
                if venue != 'Unknown':
                    # Hapus tahun dari venue jika ada
                    venue = re.sub(r'\b\d{4}\b', '', venue).strip()
                    # Hapus multiple spaces
                    venue = re.sub(r'\s+', ' ', venue)
                    # Capitalize properly
                    if len(venue) > 3 and venue.upper() != venue:
                        venue = venue.title()

                # Ekstrak metadata publikasi
                publication_data = {
                    'judul': pub_detail.get('bib', {}).get('title', 'Unknown'),
                    'jurnal_konferensi': venue,
                    'tahun': pub_year,
                    'penulis': pub_detail.get('bib', {}).get('author', 'Unknown'),
                    'kutipan': pub_detail.get('num_citations', 0)
                }
                
                publications.append(publication_data)
                print(f"  [{i+1}] {publication_data['judul'][:50]}... ({publication_data['tahun']})")
                
                # Delay untuk menghindari rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing publication {i+1}: {e}")
                continue
        
        return publications, author_name
        
    except Exception as e:
        print(f"Error mengambil data publikasi: {e}")
        return [], "Unknown"

def save_to_excel(publications, filename='output.xlsx'):
    """
    Menyimpan data publikasi ke file Excel
    
    Args:
        publications (list): Daftar publikasi
        filename (str): Nama file output
    """
    try:
        df = pd.DataFrame(publications)
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Data berhasil disimpan ke {filename}")
        print(f"Total publikasi tersimpan: {len(publications)}")
    except Exception as e:
        print(f"Error menyimpan ke Excel: {e}")

def extract_keywords_from_titles(publications):
    """
    Mengekstrak kata kunci dari judul publikasi
    
    Args:
        publications (list): Daftar publikasi
    
    Returns:
        list: Daftar kata kunci
    """
    # Gabungkan semua judul
    all_titles = ' '.join([pub['judul'] for pub in publications if pub['judul'] != 'Unknown'])
    
    # Bersihkan teks: hapus tanda baca, ubah ke lowercase, hapus angka
    cleaned_text = re.sub(r'[^\w\s]', ' ', all_titles.lower())
    cleaned_text = re.sub(r'\d+', ' ', cleaned_text)  # Hapus angka
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalisasi whitespace
    
    # Split menjadi kata-kata
    words = cleaned_text.split()
    
    # Dapatkan stopwords dari NLTK + custom academic terms
    stopwords_set = get_stopwords()
    
    # Filter kata yang panjangnya >= 4 dan bukan stopwords
    # Juga filter kata yang terlalu pendek atau hanya huruf berulang
    keywords = []
    for word in words:
        if (len(word) >= 4 and 
            word not in stopwords_set and 
            not word.isdigit() and  # Hapus angka yang tersisa
            len(set(word)) > 1):    # Hapus kata dengan huruf berulang (aaa, bbb)
            keywords.append(word)
    
    return keywords

def clean_filename(name):
    """
    Membersihkan nama untuk digunakan sebagai nama file
    
    Args:
        name (str): Nama yang akan dibersihkan
    
    Returns:
        str: Nama yang sudah dibersihkan
    """
    if not name or name == 'Unknown':
        return 'unknown_author'
    
    # Hapus karakter yang tidak valid untuk nama file
    cleaned = re.sub(r'[<>:"/\\|?*]', '', name)
    # Ganti spasi dengan underscore
    cleaned = re.sub(r'\s+', '_', cleaned)
    # Hapus karakter non-ASCII
    cleaned = re.sub(r'[^\x00-\x7F]+', '', cleaned)
    # Batas panjang nama file
    cleaned = cleaned[:50]
    # Hapus underscore di awal/akhir
    cleaned = cleaned.strip('_')
    
    return cleaned.lower() if cleaned else 'unknown_author'

def generate_filename(base_name, author_name, start_year=None, end_year=None, extension='xlsx'):
    """
    Generate filename dengan nama author dan tahun
    
    Args:
        base_name (str): Nama dasar file
        author_name (str): Nama author
        start_year (int): Tahun awal
        end_year (int): Tahun akhir
        extension (str): Ekstensi file
    
    Returns:
        str: Nama file yang sudah diformat
    """
    clean_author = clean_filename(author_name)
    
    year_suffix = ""
    if start_year and end_year and start_year != end_year:
        year_suffix = f"_{start_year}-{end_year}"
    elif start_year:
        year_suffix = f"_{start_year}"
    elif end_year:
        year_suffix = f"_-{end_year}"
    
    return f"{base_name}_{clean_author}{year_suffix}.{extension}"

def generate_wordcloud(publications, filename='wordcloud.png', start_year=None, end_year=None):
    """
    Membuat word cloud dari kata kunci dalam judul publikasi
    
    Args:
        publications (list): Daftar publikasi
        filename (str): Nama file output gambar
        start_year (int): Tahun awal publikasi untuk judul
        end_year (int): Tahun akhir publikasi untuk judul
    """
    try:
        if not publications:
            print("Tidak ada publikasi untuk dibuat word cloud")
            return
        
        # Ekstrak kata kunci
        keywords = extract_keywords_from_titles(publications)
        
        if not keywords:
            print("Tidak ada kata kunci yang ditemukan")
            return
        
        # Hitung frekuensi kata
        word_freq = Counter(keywords)
        
        # Buat word cloud
        wordcloud = WordCloud(
            width=800, 
            height=400, 
            background_color='white',
            max_words=100,
            colormap='viridis'
        ).generate_from_frequencies(word_freq)
        
        # Plot dan simpan
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        year_text = ""
        if start_year and end_year:
            year_text = f" ({start_year}-{end_year})"
        elif start_year:
            year_text = f" ({start_year}+)"
        elif end_year:
            year_text = f" (-{end_year})"
        plt.title(f'Word Cloud Kata Kunci Publikasi{year_text}', fontsize=16, pad=20)
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Word cloud berhasil disimpan ke {filename}")
        
        # Tampilkan statistik kata teratas
        print("\nKata kunci teratas:")
        for word, freq in word_freq.most_common(10):
            print(f"  {word}: {freq}")
        
    except Exception as e:
        print(f"Error membuat word cloud: {e}")

def main():
    """
    Fungsi utama program
    """
    parser = argparse.ArgumentParser(description='Google Scholar Publication Crawler')
    parser.add_argument('scholar_id', help='ID Google Scholar (contoh: CJMh47UAAAAJ)')
    parser.add_argument('--start-year', type=int, help='Tahun awal publikasi (contoh: 2020)')
    parser.add_argument('--end-year', type=int, help='Tahun akhir publikasi (contoh: 2023)')
    parser.add_argument('--year', type=int, help='Tahun publikasi tunggal (contoh: 2022) - akan diabaikan jika start-year/end-year digunakan')
    parser.add_argument('--output', default='output.xlsx', help='Nama file Excel output')
    parser.add_argument('--wordcloud', default='wordcloud.png', help='Nama file word cloud output')
    
    args = parser.parse_args()
    
    print("="*60)
    print("GOOGLE SCHOLAR PUBLICATION CRAWLER")
    print("="*60)
    print(f"Scholar ID: {args.scholar_id}")
    
    # Tentukan parameter tahun
    start_year = None
    end_year = None
    
    if getattr(args, 'start_year', None):
        start_year = args.start_year
    if getattr(args, 'end_year', None):
        end_year = args.end_year
    
    # Fallback ke --year jika tidak ada start/end year
    if not start_year and not end_year and args.year:
        start_year = end_year = args.year
    
    if start_year and end_year:
        print(f"Rentang Tahun: {start_year}-{end_year}")
    elif start_year:
        print(f"Tahun Awal: {start_year}")
    elif end_year:
        print(f"Tahun Akhir: {end_year}")
    print()
    
    # Ambil data publikasi
    publications, author_name = get_author_publications(args.scholar_id, start_year, end_year)
    
    if not publications:
        print("Tidak ada publikasi yang ditemukan!")
        sys.exit(1)
    
    print(f"\nBerhasil mengambil {len(publications)} publikasi")
    
    # Generate filename dengan nama author
    excel_filename = generate_filename('publications', author_name, start_year, end_year, 'xlsx')
    wordcloud_filename = generate_filename('wordcloud', author_name, start_year, end_year, 'png')
    
    # Override jika user memberikan custom filename
    if args.output != 'output.xlsx':
        excel_filename = args.output
    if args.wordcloud != 'wordcloud.png':
        wordcloud_filename = args.wordcloud
    
    # Simpan ke Excel
    print("\nMenyimpan data ke Excel...")
    save_to_excel(publications, excel_filename)
    
    # Buat word cloud
    print("\nMembuat word cloud...")
    generate_wordcloud(publications, wordcloud_filename, start_year, end_year)
    
    print("\nProses selesai!")
    print(f"File yang dihasilkan:")
    print(f"  - {excel_filename}")
    print(f"  - {wordcloud_filename}")

if __name__ == "__main__":
    main()