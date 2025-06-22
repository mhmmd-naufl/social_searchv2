import time
from selenium_driver import setup_selenium_driver
from add_cookie import add_cookies_to_driver
from cookies import cookie
from video_scrapper import scrape_video_detail
from comment_scrapper import scrape_comments
from sentiment_analyzer import SentimentAnalyzer
from data_processor import DataProcessor
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_and_analyze_tiktok(keyword, num_videos=6):
    from urllib.parse import quote_plus
    url = f"https://www.tiktok.com/search?q={quote_plus(keyword)}"
    driver = setup_selenium_driver()
    add_cookies_to_driver(driver, cookie)
    driver.get(url)
    time.sleep(3)
    video_card_xpath = "//div[@data-e2e='search_top-item']//a[contains(@href, '/video/')]"
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, video_card_xpath))
    )
    video_cards = driver.find_elements(By.XPATH, video_card_xpath)
    print(f"Ditemukan {len(video_cards)} video di hasil pencarian.")

    sentiment_analyzer = SentimentAnalyzer()
    data_processor = DataProcessor()

    for idx in range(min(num_videos, len(video_cards))):
        print(f"\n--- Memproses Video ke-{idx+1} ---")
        # Ambil ulang elemen karena DOM bisa berubah setelah back
        video_cards = driver.find_elements(By.XPATH, video_card_xpath)
        card = video_cards[idx]
        driver.execute_script("arguments[0].scrollIntoView();", card)
        time.sleep(1)
        card.click()
        time.sleep(3)
        video_data = scrape_video_detail(driver)
        comments = scrape_comments(driver, max_comments=100)
        processed_comments = []
        for c in comments:
            sentiment = sentiment_analyzer.analyze_sentiment(c['text'])
            processed_comments.append({
                **c,
                "sentiment": sentiment
            })
        data_processor.add_video_comments_with_sentiment(video_data, processed_comments)
        driver.back()
        time.sleep(2)

    driver.quit()
    data_processor.save_to_json("tiktok_search_comments_with_sentiment.json")
    print("Selesai.")
    return data_processor.get_data()

if __name__ == "__main__":
    keyword = "banyuwangi"
    scrape_and_analyze_tiktok(keyword, num_videos=6)
    print("Data telah disimpan ke tiktok_search_comments_with_sentiment.json")