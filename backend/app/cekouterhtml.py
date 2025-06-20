import time
import random
import json
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium_driver import setup_selenium_driver
from add_cookie import add_cookies_to_driver
from cookies import cookie as cookies_str

def random_delay(a=1, b=3):
    time.sleep(random.uniform(a, b))

def wait_for_page_load(driver):
    for _ in range(30):
        if driver.execute_script("return document.readyState") == "complete":
            break
        time.sleep(1)
    time.sleep(2)

def find_comment_selector(driver):
    selectors = [
        'div[data-e2e="comment-item"]',
        'div[class*="comment"]',
        '[data-e2e*="comment"]',
        'div[class="css-x4xlc7-DivCommentContainer ejcng160"]'
    ]
    for sel in selectors:
        elems = driver.find_elements(By.CSS_SELECTOR, sel)
        if elems:
            return sel
    return None

def scroll_and_collect_comments(driver, selector, max_comments=20, max_scroll=10):
    comments = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scroll):
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elems:
                try:
                    text = ""
                    for ts in ['p[data-e2e="comment-level-1"]', 'span[data-e2e="comment-level-1"]', 'p', 'span']:
                        try:
                            text = elem.find_element(By.CSS_SELECTOR, ts).text.strip()
                            if text: break
                        except: continue
                    if not text:
                        text = elem.text.strip()
                    if text and not any(c["comment"] == text for c in comments):
                        comments.append({"index": len(comments)+1, "comment": text})
                        if len(comments) >= max_comments:
                            return comments
                except (NoSuchElementException, StaleElementReferenceException):
                    continue
        except StaleElementReferenceException:
            continue
        driver.execute_script("window.scrollBy(0, 500);")
        random_delay(1, 2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    return comments

def cek():
    driver = setup_selenium_driver()
    try:
        url = "https://www.tiktok.com/@poppyfara/video/7450756249769020677"
        if cookies_str:
            add_cookies_to_driver(driver, cookies_str)
        driver.get(url)
        wait_for_page_load(driver)
        random_delay(2, 4)
        selector = find_comment_selector(driver)
        if not selector:
            print("Selector komentar tidak ditemukan.")
            driver.save_screenshot("debug_screenshot.png")
            return
        comments = scroll_and_collect_comments(driver, selector)
        print(f"Total komentar diambil: {len(comments)}")
        if comments:
            with open("comments_result.json", "w", encoding="utf-8") as f:
                json.dump(comments, f, ensure_ascii=False, indent=2)
            print("Komentar disimpan ke comments_result.json")
        else:
            print("Tidak ada komentar yang berhasil diambil")
    except Exception as e:
        print(f"Terjadi error: {e}")
        driver.save_screenshot("error_screenshot.png")
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Memulai scraping komentar TikTok...")
    cek()
    print("Selesai.")