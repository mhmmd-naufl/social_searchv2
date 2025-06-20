import pandas as pd
import re
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import json

INPUT_JSON_FILE = 'csvjson.json'
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
    'inspiratif': 1, 'menghibur': 1, 'mendidik': 1, 'setuju': 1, 'asli': 1, 'lanjut': 1,
    'kocak': 1, 'lucu': 1, 'ngakak': 1, 'respect': 1, 'salut': 1, 'legend': 1,
    'jenius': 1, 'kreatif': 1, 'relate': 1, 'idola': 1, 'bagus_banget': 1,
    'terbaik': 1, 'terharu': 1, 'niat': 1, 'ramah': 1, 'bijak': 1, 'bermanfaat': 1,
    'cocok': 1, 'jujur': 1, 'rapih': 1, 'estetik': 1, 'wow': 1, 'cakep': 1, 'good': 1,
    'sip': 1, 'oke': 1, 'ya': 1, 'boleh': 1, 'mungkin': 1, 'santai': 1, 'goks': 1,
    'gaskeun': 1, 'auto': 1, 'semangat': 1, 'pejuang': 1, 'nice' : 1,
    '❤️': 1, '😍': 1, '🥰': 1, '🔥': 1, '👏': 1, '👍': 1, '💪': 1, '😁': 1, '🤩': 1,

    'jelek': -1, 'buruk': -1, 'benci': -1, 'kesal': -1, 'marah': -1, 'kecewa': -1,
    'parah': -1, 'rugi': -1, 'tidak_suka': -1, 'negatif': -1, 'sampah': -1,
    'nyesel': -1, 'lebay': -1, 'alay': -1, 'lebai': -1, 'cringe': -1,
    'gagal': -1, 'sakit': -1, 'toxic': -1, 'capek': -1, 'malas': -1,
    'basi': -1, 'ngaco': -1, 'aneh': -1, 'serem': -1, 'pelit': -1,
    'curang': -1, 'fake': -1, 'palsu': -1, 'anjing': -1, 'provokatif': -1,
    'males': -1, 'skip': -1, 'garing': -1, 'emosi': -1, 'bangsat': -1,
    'kampret': -1, 'tolol': -1, 'bodoh': -1, 'goblok': -1, 'kampungan': -1,
    'ngeselin': -1, 'menjijikkan': -1, 'nolep': -1, 'julid': -1,
    'ngedumel': -1, 'menyeramkan': -1,
    '💩': -1, '😡': -1, '👎': -1, '😠': -1, '🤮': -1,
} 

def analyze_sentiment_lexicon(text_tokens, lexicon):
    score = 0
    for token in text_tokens:
        score += lexicon.get(token, 0)
    
    if score > 0:
        return 'positif'
    elif score < 0:
        return 'negatif'
    else:
        return 'netral'

try:
    with open(INPUT_JSON_FILE, 'r', encoding='utf-8') as f:
        data_json = json.load(f)
    
    print(f"Berhasil memuat '{INPUT_JSON_FILE}'.")
    print(f"Jumlah entri awal: {len(data_json)}")

    comments_data = []
    for item in data_json:
        if KOMENTAR_KEY_IN_JSON in item and isinstance(item[KOMENTAR_KEY_IN_JSON], str):
            row_data = item.copy()
            comments_data.append(row_data)
    
    df_komentar = pd.DataFrame(comments_data)
    
    if df_komentar.empty:
        raise ValueError(f"Tidak ada komentar yang ditemukan pada kunci '{KOMENTAR_KEY_IN_JSON}' atau data kosong setelah filter.")

    df_komentar[KOMENTAR_KEY_IN_JSON] = df_komentar[KOMENTAR_KEY_IN_JSON].astype(str)
    df_komentar.dropna(subset=[KOMENTAR_KEY_IN_JSON], inplace=True)
    df_komentar.reset_index(drop=True, inplace=True)
    print(f"Jumlah komentar setelah memfilter dan menghapus nilai kosong: {len(df_komentar)}")

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