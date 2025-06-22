from fastapi import FastAPI, HTTPException
from scrapper import search_video
from pymongo import MongoClient
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # atau ganti dengan ['http://localhost:3000'] jika frontend di port 3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def fix_objectid(data):
    if isinstance(data, list):
        return [fix_objectid(item) for item in data]
    elif isinstance(data, dict):
        return {k: str(v) if isinstance(v, ObjectId) else fix_objectid(v) for k, v in data.items()}
    else:
        return data

MONGO_URI = "mongodb://localhost:27017"
client = MongoClient(MONGO_URI)
db = client["new_tiktok_db"]
collection = db["videos"]

def check_keyword_in_db(keyword: str) -> bool:
    try:
        result = collection.find_one({"keyword": keyword})
        return result is not None
    except Exception as e:
        print(f"Database error: {e}")
        return False

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI!"}

@app.get("/search")
async def search(keyword: str):
    if not keyword:
        raise HTTPException(status_code=400, detail="Keyword is required")

    # Cek apakah keyword sudah ada di database
    if check_keyword_in_db(keyword):
        data = list(collection.find({"keyword": keyword}))
        data = fix_objectid(data)
        return {"status": "success", "data": data}
    else:
        try:
            # Jika tidak ada, jalankan scrapper
            result = search_video(keyword)
            if result:
                result = fix_objectid(result)
                return {"status": "success", "data": result}
            else:
                raise HTTPException(status_code=404, detail="No data found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Scrapper failed: {str(e)}")