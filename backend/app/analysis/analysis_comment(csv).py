import nltk
import pandas as pd
import re
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import numpy as np

nltk.download('stopwords')

# --- 1. Konfigurasi File Input dan Output ---
INPUT_CSV_FILE = 'komen.csv' # Ganti dengan nama file CSV Anda
OUTPUT_CSV_FILE_LEXICON = 'komentar_tiktok_sentimen_lexicon.csv' # Nama file output untuk hasil sentimen
KOMENTAR_COLUMN = 'comment_text' # Ganti jika nama kolom komentar Anda berbeda

# --- 2. Pra-pemrosesan Teks ---
def preprocess_text(text):
    if not isinstance(text, str): # Pastikan input adalah string, tangani NaN atau tipe lain
        return ""
    
    text = text.lower() # Case folding
    text = re.sub(r'[^a-zA-Z\s]', '', text) # Hapus angka dan tanda baca (sisakan huruf dan spasi)
    tokens = text.split() # Tokenisasi
    
    # Hapus stop words bahasa Indonesia
    list_stopwords = set(stopwords.words('indonesian'))
    tokens = [word for word in tokens if word not in list_stopwords]
    
    # Stemming dengan Sastrawi
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    tokens = [stemmer.stem(word) for word in tokens]
    
    return tokens # Mengembalikan list token karena kita akan memprosesnya per kata

# --- 3. Leksikon Sentimen (Sangat Sederhana - Perlu Ditingkatkan!) ---
# Ini adalah contoh leksikon. Anda perlu membangun leksikon yang lebih komprehensif
# atau mencari leksikon bahasa Indonesia yang sudah ada.
# Format: {kata_dasar: skor_sentimen}
# Skor positif = +1, Negatif = -1, Netral = 0 (kata yang tidak ada di leksikon dianggap netral)

lexicon = {
    'bagus': 1, 'baik': 1, 'suka': 1, 'senang': 1, 'cinta': 1, 'hebat': 1, 'mantap': 1,
    'keren': 1, 'luar_biasa': 1, 'top': 1, 'asik': 1, 'menarik': 1, 'positif': 1,
    'jelek': -1, 'buruk': -1, 'benci': -1, 'kesal': -1, 'marah': -1, 'kecewa': -1,
    'parah': -1, 'rugi': -1, 'tidak_suka': -1, 'negatif': -1, 'sampah': -1,
    'biasa': 0, 'lumayan': 0, 'cukup': 0, 'ok': 0, 'standar': 0, 'normal': 0
}

def analyze_sentiment_lexicon(text_tokens, lexicon):
    score = 0
    for token in text_tokens:
        score += lexicon.get(token, 0) # Tambahkan skor kata, jika tidak ada di leksikon, skor 0
    
    # Klasifikasi sentimen berdasarkan skor total
    if score > 0:
        return 'positif'
    elif score < 0:
        return 'negatif'
    else:
        return 'netral'

# --- 4. Memuat Data dari CSV ---
try:
    df_komentar = pd.read_csv(INPUT_CSV_FILE)
    print(f"Berhasil memuat '{INPUT_CSV_FILE}'.")
    print(f"Jumlah komentar awal: {len(df_komentar)}")
    
    if KOMENTAR_COLUMN not in df_komentar.columns:
        raise ValueError(f"Kolom '{KOMENTAR_COLUMN}' tidak ditemukan di file CSV Anda.")
    
    df_komentar.dropna(subset=[KOMENTAR_COLUMN], inplace=True)
    df_komentar.reset_index(drop=True, inplace=True)
    print(f"Jumlah komentar setelah menghapus nilai kosong: {len(df_komentar)}")

    # Pra-pemrosesan komentar dan simpan sebagai list token
    print("Memulai pra-pemrosesan teks...")
    df_komentar['komentar_tokenized'] = df_komentar[KOMENTAR_COLUMN].apply(preprocess_text)
    print("Pra-pemrosesan teks selesai.")
    
except FileNotFoundError:
    print(f"Error: File '{INPUT_CSV_FILE}' tidak ditemukan. Pastikan file berada di direktori yang sama dengan script ini, atau berikan path lengkap.")
    exit()
except ValueError as e:
    print(f"Error: {e}")
    exit()
except Exception as e:
    print(f"Terjadi kesalahan saat memuat atau memproses file: {e}")
    exit()

# --- 5. Menganalisis Sentimen Menggunakan Leksikon ---
print("\nMemulai analisis sentimen berbasis leksikon...")
df_komentar['sentimen'] = df_komentar['komentar_tokenized'].apply(lambda x: analyze_sentiment_lexicon(x, lexicon))
print("Analisis sentimen selesai.")

# --- 6. Ringkasan Hasil ---
print("\n--- Ringkasan Hasil Analisis Sentimen Berbasis Leksikon ---")
print(df_komentar['sentimen'].value_counts())

# --- 7. Menyimpan Hasil ke File CSV Baru ---
print(f"\nMenyimpan hasil analisis ke '{OUTPUT_CSV_FILE_LEXICON}'...")
# Kita bisa hilangkan kolom 'komentar_tokenized' jika tidak diperlukan di output
df_komentar_output = df_komentar.drop(columns=['komentar_tokenized'])
df_komentar_output.to_csv(OUTPUT_CSV_FILE_LEXICON, index=False)
print("Selesai! File output berhasil dibuat.")

print(f"\nAnda bisa melihat komentar asli dan hasil sentimen di file '{OUTPUT_CSV_FILE_LEXICON}'.")

# --- Contoh Prediksi Manual ---
print("\n--- Coba prediksi sentimen komentar baru (manual) ---")
contoh_komentar_baru = [
    "Wah, videonya inspiratif banget!",       # Mengandung 'inspiratif' (tidak di leksikon), 'banget' (tidak di leksikon) -> mungkin netral
    "Parah, ini bikin aku emosi.",           # Mengandung 'parah' -> negatif
    "Biasa aja sih, nggak ada yang istimewa.", # Mengandung 'biasa' -> netral
    "Keren banget, aku suka!",               # Mengandung 'keren', 'suka' -> positif
    "Kontennya buruk sekali."                # Mengandung 'buruk' -> negatif
]

for komentar in contoh_komentar_baru:
    cleaned_tokens = preprocess_text(komentar)
    predicted_sentiment = analyze_sentiment_lexicon(cleaned_tokens, lexicon)
    print(f"'{komentar}' (Kata dasar: {cleaned_tokens}) -> Sentimen: {predicted_sentiment}")