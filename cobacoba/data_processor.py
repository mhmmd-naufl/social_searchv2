# data_processor.py
import json

class DataProcessor:
    def __init__(self):
        self.all_scraped_data = [] # Untuk menyimpan semua data yang sudah digabungkan

    def add_video_comments_with_sentiment(self, video_data, comments_with_sentiment):
        """
        Menambahkan data video dan komentar yang sudah dianalisis sentimennya.
        :param video_data: Dictionary berisi info video (desc, author, link, id, keyword).
        :param comments_with_sentiment: List of dictionaries, setiap dict berisi {'comment_id', 'text', 'sentiment'}.
        """
        entry = video_data.copy() # Salin data video
        entry['comments_analyzed'] = comments_with_sentiment
        self.all_scraped_data.append(entry)

    def save_to_json(self, filename):
        """
        Menyimpan semua data yang terkumpul ke file JSON.
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.all_scraped_data, f, ensure_ascii=False, indent=4)
            print(f"Data berhasil disimpan ke '{filename}'.")
        except Exception as e:
            print(f"Gagal menyimpan data ke JSON: {e}")

    def get_data(self):
        """Mengembalikan data yang saat ini tersimpan."""
        return self.all_scraped_data