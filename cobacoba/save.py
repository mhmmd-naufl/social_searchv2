from pymongo import MongoClient

def save_to_mongo(data):
    db_name="new_tiktok_db"
    mongo_uri="mongodb://localhost:27017"
    collection_name="videos"
    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]
        collection.insert_one(data)
        print("Data berhasil disimpan ke MongoDB.")
    except Exception as e:
        print(f"Error saat menyimpan ke MongoDB: {e}")
    finally:
        client.close()
