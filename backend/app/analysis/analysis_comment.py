import re
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# --- 1. Pra-pemrosesan Teks ---
def preprocess_text(text):
    if not isinstance(text, str):
        return []
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    tokens = text.split()
    list_stopwords = set(stopwords.words('indonesian'))
    tokens = [word for word in tokens if word not in list_stopwords]
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    tokens = [stemmer.stem(word) for word in tokens]
    return tokens

# --- 2. Leksikon Sentimen ---
lexicon = {
    # positif words
    'bagus': 1, 'baik': 1, 'suka': 1, 'senang': 1, 'cinta': 1, 'hebat': 1, 'mantap': 1,
    'keren': 1, 'luar_biasa': 1, 'top': 1, 'asik': 1, 'menarik': 1, 'positif': 1,
    'indah': 1, 'sehat': 1, 'bahagia': 1, 'adil': 1, 'tenang': 1, 'tenteram': 1, 
    'sukses': 1, 'berhasil': 1, 'mulia': 1, 'luhur': 1, 'cerdas': 1, 'pandai': 1, 'jujur': 1, 'setia': 1, 
    'mujur': 1, 'manis': 1, 'enak': 1, 'nikmat': 1, 'patut': 1, 'layak': 1, 'sempurna': 1, 
    'kuat': 1, 'berani': 1, 'lincah': 1, 'cepat': 1, 'rapi': 1, 'bersih': 1, 'murni': 1, 'suci': 1, 
    'damai': 1, 'harmoni': 1, 'modern': 1, 'unggul': 1, 'utama': 1, 'terbaik': 1, 'cemerlang': 1, 
    'menyenangkan': 1, 'membanggakan': 1, 'memukau': 1, 'menakjubkan': 1, 'ramah': 1, 
    'sopan': 1, 'murah hati': 1, 'dermawan': 1, 'bijaksana': 1, 'kreatif': 1, 'inovatif': 1, 
    'inspiratif': 1, 'motivasi': 1, 'optimis': 1, 'ceria': 1, 'gembira': 1, 'antusias': 1, 
    'dinamis': 1, 'elegan': 1, 'anggun': 1, 'menawan': 1, 'cantik': 1, 'rupawan': 1, 'elok': 1, 
    'megah': 1, 'mewah': 1, 'berkilau': 1, 'bercahaya': 1, 'cerah': 1, 'menyegarkan': 1, 
    'menenangkan': 1, 'nyaman': 1, 'aman': 1, 'stabil': 1, 'makmur': 1, 'sejahtera': 1, 
    'beruntung': 1, 'berkualitas': 1, 'terpuji': 1, 'terhormat': 1, 'berwibawa': 1, 'berprestasi': 1, 
    'efektif': 1, 'efisien': 1, 'produktif': 1, 'progresif': 1, 'maju': 1, 'berkembang': 1, 
    'harmonis': 1, 'damai': 1, 'penuh kasih': 1, 'sayang': 1, 'peduli': 1, 'empati': 1, 
    'berbudi': 1, 'luhur': 1, 'agung': 1, 'mengagumkan': 1, 'fenomenal': 1, 'luar biasa': 1, 'spektakuler': 1, 'memesona': 1,
    '🤣': 1, '😂': 1, '😭': 1, '🥰': 1, 'semangat': 1, 
    
    # negative words
    'sakit': -1, 'sedih': -1, 'cemas': -1, 'khawatir': -1, 'bodoh': -1, 'tolol': -1, 
    'malas': -1, 'sial': -1, 'celaka': -1, 'rusak': -1, 'hancur': -1, 'miskin': -1, 'kotor': -1, 'kasar': -1, 
    'jahat': -1, 'kejam': -1, 'sombong': -1, 'congkak': -1, 'lambat': -1, 'lemah': -1, 'cacat': -1, 'gagal': -1, 
    'susah': -1, 'sulit': -1, 'kacau': -1, 'berantakan': -1, 'dengki': -1, 'jengkel': -1, 'putus asa': -1,
    'kurang': -1, 'rendah': -1, 'hina': -1, 'malu': -1, 'mengerikan': -1, 'menyedihkan': -1, 
    'menjijikkan': -1, 'menakutkan': -1, 'meresahkan': -1, 'mengganggu': -1, 'menyusahkan': -1, 
    'berbahaya': -1, 'mematikan': -1, 'jahil': -1, 'nakal': -1, 'culas': -1, 'curang': -1, 'licik': -1, 
    'khianat': -1, 'pengkhianat': -1, 'munafik': -1, 'palsu': -1, 'bohong': -1, 'penipu': -1, 'korupsi': -1, 
    'busuk': -1, 'lapuk': -1, 'usang': -1, 'kuno': -1, 'terbelakang': -1, 'terpuruk': -1, 'menderita': -1, 
    'sengsara': -1, 'payah': -1, 'lelet': -1, 'kusam': -1, 'suram': -1, 'kelam': -1, 'gelap': -1, 'muram': -1, 
    'lesu': -1, 'letih': -1, 'capek': -1, 'lelah': -1, 'bosan': -1, 'jenuh': -1, 'muak': -1, 'risih': -1, 
    'geram': -1, 'sebal': -1, 'dongkol': -1, 'gregetan': -1, 'sakit hati': -1, 'patah hati': -1, 
    'putus harapan': -1, 'terhina': -1, 'tercela': -1, 'terkutuk': -1, 'terlantar': -1, 
    'terabaikan': -1, 'tersisih': -1, 'termarginalkan': -1, 'tertekan': -1, 'terhambat': -1, 
    'tertutup': -1, 'terisolasi': -1, 'terasing': -1, 'jelek': -1, 'buruk': -1, 'benci': -1, 
    'kesal': -1, 'marah': -1, 'kecewa': -1, 'parah': -1, 'rugi': -1, 
    'tidak_suka': -1, 'negatif': -1, 'sampah': -1,
    
    # neutral words
    'biasa': 0, 'lumayan': 0, 'cukup': 0, 'ok': 0, 'standar': 0, 'normal': 0
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

# --- 3. Analisis Sentimen Komentar dari Data Scrapper ---
def analyze_comments_from_data(data, lexicon):
    analyzed_comments = []
    for comment in data:
        tokens = preprocess_text(comment)
        sentiment = analyze_sentiment_lexicon(tokens, lexicon)
        analyzed_comments.append({
            "text": comment,
            "sentiment": sentiment
        })
    return analyzed_comments

# --- 4. Contoh Penggunaan Mandiri ---
# if __name__ == "__main__":
#     # Contoh data hasil scrapper
#     final_result = [
#         {
#             "desc": "Contoh desc",
#             "author": "user1",
#             "video_link": "https://tiktok.com/@user1/video/123",
#             "video_id": "123",
#             "keyword": "banyuwangi",
#             "comment": [
#                 "Infoin kafe Banyuwangi kota yg 24 jam dongg",
#                 "kenapa klo bagus jauh dari kota 😌"
#             ]
#         }
#     ]
#     hasil = analyze_comments_from_data(final_result, lexicon)
#     import json
#     print(json.dumps(hasil, ensure_ascii=False, indent=2))