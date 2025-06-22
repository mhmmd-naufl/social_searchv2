import json

class DataProcessor:
    def __init__(self):
        self.data = []
    def add_video_comments_with_sentiment(self, video_data, comments):
        self.data.append({**video_data, "comments": comments})
    def save_to_json(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
    def get_data(self):
        return self.data