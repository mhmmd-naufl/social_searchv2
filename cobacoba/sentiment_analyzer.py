# sentiment_analyzer.py
import re
from nltk.corpus import stopwords
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import nltk

# Unduh stop words (jalankan sekali jika belum ada)
# Pastikan Anda sudah menjalankan:
# import nltk
# nltk.download('stopwords')
try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    nltk.download('stopwords')

class SentimentAnalyzer:
    def __init__(self):
        self.stemmer_factory = StemmerFactory()
        self.stemmer = self.stemmer_factory.create_stemmer()
        self.list_stopwords = set(stopwords.words('indonesian'))
        
        # Leksikon Sentimen (BISA DIKEMBANGKAN LEBIH LANJUT SESUAI KEBUTUHAN ANDA)
        self.lexicon = {
            'bagus': 1, 'baik': 1, 'suka': 1, 'senang': 1, 'cinta': 1, 'hebat': 1, 'mantap': 1,
            'keren': 1, 'luar_biasa': 1, 'top': 1, 'asik': 1, 'menarik': 1, 'positif': 1,
            'inspiratif': 1, 'menghibur': 1, 'mendidik': 1, 'setuju': 1, 'asli': 1, 'lanjut': 1,
            
            'jelek': -1, 'buruk': -1, 'benci': -1, 'kesal': -1, 'marah': -1, 'kecewa': -1,
            'parah': -1, 'rugi': -1, 'tidak_suka': -1, 'negatif': -1, 'sampah': -1,
            'emosi': -1, 'nyesel': -1, 'sakit': -1, 'buang': -1, 'basi': -1,
            
            'biasa': 0, 'lumayan': 0, 'cukup': 0, 'ok': 0, 'standar': 0, 'normal': 0,
            'mutu': 0, 'greget': 0, 'spesial': 0, 'mata': 0, 'jiwa': 0,
        }

    def preprocess_text(self, text):
        """Membersihkan dan menokenisasi teks."""
        if not isinstance(text, str):
            return ""
        
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text) # Hapus non-alfabet
        tokens = text.split()
        
        tokens = [word for word in tokens if word not in self.list_stopwords]
        tokens = [self.stemmer.stem(word) for word in tokens]
        
        return tokens

    def analyze_sentiment(self, text):
        """
        Menganalisis sentimen dari teks menggunakan leksikon.
        Mengembalikan 'positif', 'negatif', atau 'netral'.
        """
        tokens = self.preprocess_text(text)
        score = 0
        for token in tokens:
            score += self.lexicon.get(token, 0)
        
        if score > 0:
            return 'positif'
        elif score < 0:
            return 'negatif'
        else:
            return 'netral'