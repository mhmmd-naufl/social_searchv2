import pandas as pd
import re
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import json

# --- 1. Konfigurasi File Input dan Output ---
INPUT_JSON_FILE = 'csvjson.json' # Ganti dengan nama file JSON Anda
OUTPUT_JSON_FILE_LEXICON = 'komentar_tiktok_sentimen_output.json' # Nama file output untuk hasil sentimen (JSON)
KOMENTAR_KEY_IN_JSON = 'comment_text' # <--- PENTING: Ganti dengan nama key yang berisi komentar di JSON Anda

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
    'biasa': 0, 'lumayan': 0, 'cukup': 0, 'ok': 0, 'standar': 0, 'normal': 0,
    'inspiratif': 1, 'menghibur': 1, 'mendidik': 1, 'mutu': 0, 'emosi': -1,
    'greget': 0, 'setuju': 1, 'spesial': 0, 'kecewa': -1, 'asli': 1, 'nyesel': -1,
    'sakit': -1, 'mata': 0, 'biasa': 0, 'jiwa': 0, 'lanjut': 1
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

# --- 4. Memuat Data dari JSON ---
try:
    with open(INPUT_JSON_FILE, 'r', encoding='utf-8') as f:
        data_json = json.load(f)
    
    print(f"Berhasil memuat '{INPUT_JSON_FILE}'.")
    print(f"Jumlah entri awal: {len(data_json)}")

    # Konversi data JSON ke DataFrame pandas
    # Pastikan data yang diekstrak adalah string
    comments_data = []
    for item in data_json:
        if KOMENTAR_KEY_IN_JSON in item and isinstance(item[KOMENTAR_KEY_IN_JSON], str):
            # Tambahkan semua key-value pair dari item asli, lalu tambahkan sentimen nanti
            # Ini akan menjaga struktur asli JSON sejauh mungkin
            row_data = item.copy() # Salin item asli
            comments_data.append(row_data)
    
    df_komentar = pd.DataFrame(comments_data)
    
    if df_komentar.empty:
        raise ValueError(f"Tidak ada komentar yang ditemukan pada kunci '{KOMENTAR_KEY_IN_JSON}' atau data kosong setelah filter.")

    # Pastikan kolom komentar yang akan diproses adalah string
    df_komentar[KOMENTAR_KEY_IN_JSON] = df_komentar[KOMENTAR_KEY_IN_JSON].astype(str)
    df_komentar.dropna(subset=[KOMENTAR_KEY_IN_JSON], inplace=True)
    df_komentar.reset_index(drop=True, inplace=True)
    print(f"Jumlah komentar setelah memfilter dan menghapus nilai kosong: {len(df_komentar)}")

    # Pra-pemrosesan komentar dan simpan sebagai list token
    print("Memulai pra-pemrosesan teks...")
    df_komentar['komentar_tokenized'] = df_komentar[KOMENTAR_KEY_IN_JSON].apply(preprocess_text)
    print("Pra-pemrosesan teks selesai.")
    
except FileNotFoundError:
    print(f"Error: File '{INPUT_JSON_FILE}' tidak ditemukan. Pastikan file berada di direktori yang sama dengan script ini, atau berikan path lengkap.")
    exit()
except json.JSONDecodeError:
    print(f"Error: File '{INPUT_JSON_FILE}' bukan JSON yang valid.")
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

# --- 7. Menyimpan Hasil ke File JSON Baru ---
print(f"\nMenyimpan hasil analisis ke '{OUTPUT_JSON_FILE_LEXICON}'...")
# Kita bisa hilangkan kolom 'komentar_tokenized' sebelum menyimpan
df_komentar_output = df_komentar.drop(columns=['komentar_tokenized'])

# Simpan ke JSON dalam format list of dictionaries (records)
df_komentar_output.to_json(OUTPUT_JSON_FILE_LEXICON, orient='records', indent=4, force_ascii=False)
print("Selesai! File output JSON berhasil dibuat.")

print(f"\nAnda bisa melihat komentar asli dan hasil sentimen di file '{OUTPUT_JSON_FILE_LEXICON}'.")

# --- Contoh Prediksi Manual (untuk debugging/verifikasi) ---
print("\n--- Coba prediksi sentimen komentar baru (manual) ---")
contoh_komentar_baru = [
    "Wah, videonya inspiratif banget!",       
    "Parah, ini bikin aku emosi.",           
    "Biasa aja sih, nggak ada yang istimewa.", 
    "Keren banget, aku suka!",               
    "Kontennya buruk sekali."                
]

for komentar in contoh_komentar_baru:
    cleaned_tokens = preprocess_text(komentar)
    predicted_sentiment = analyze_sentiment_lexicon(cleaned_tokens, lexicon)
    print(f"'{komentar}' (Kata dasar: {cleaned_tokens}) -> Sentimen: {predicted_sentiment}")