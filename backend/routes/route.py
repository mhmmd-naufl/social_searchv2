from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from app.scrapper import search_video

app = FastAPI()

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

    # Check if keyword exists in database
    if check_keyword_in_db(keyword):
        return {"message": f"Keyword '{keyword}' found in database"}
    else:
        try:
            # Run the scrapper function if keyword is not in database
            hasil = search_video(keyword)
            return {
                "message": f"Keyword '{keyword}' not found in database, scrapper executed",
                "data": hasil
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Scrapper failed: {str(e)}")