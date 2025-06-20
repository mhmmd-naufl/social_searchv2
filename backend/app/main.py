from fastapi import FastAPI, HTTPException
from scrapper import search_video
from pymongo import MongoClient
from bson import ObjectId

# if __name__ == "__main__":  
#     print("Memulai...")
#     search_video("banyuwangi")
#     print("\nselesai.")
    
app = FastAPI()

def fix_objectid(data):
    if isinstance(data, list):
        return [fix_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {k: str(v) if isinstance(v, ObjectId) else fix_objectid(v) for k, v in data.items()}
    else:
        return data

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["tiktok_db"]
collection = db["search_results"]

def check_keyword_in_db(keyword: str) -> bool:
    try:
        result = collection.find_one({"keyword": keyword})
        return result is not None
    except Exception as e:
        print(f"Database error: {e}")
        return False

@app.get("/search")
async def search(keyword: str):
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword is required")

    if check_keyword_in_db(keyword):
        return {"message": f"Keyword '{keyword}' found in database"}
    else:
        try:
            result = search_video(keyword)
            if result:
                result = fix_objectid(result)
                return {"status": "success", "data": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Scrapper failed: {str(e)}")