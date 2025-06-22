import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from analysis.analysis_comment import analyze_comments_from_data, lexicon

def random_delay(min_delay=1, max_delay=3):
    time.sleep(random.uniform(min_delay, max_delay))

def wait_for_page_load(driver):
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(2)

def find_comment_selectors(driver):
    selector = 'span[data-e2e="comment-level-1"]'
    elements = driver.find_elements(By.CSS_SELECTOR, selector)
    if elements:
        print(f"Ditemukan {len(elements)} elemen dengan selector: {selector}")
        return selector
    return None

def cek(driver, video_data):
    try:
        url = video_data["video_link"]
        driver.get(url)
        random_delay(2, 4)
        print(f"Mengunjungi URL: {url}")
        wait_for_page_load(driver)
        comment_selector = find_comment_selectors(driver)
        if not comment_selector:
            time.sleep(5)
            comment_selector = find_comment_selectors(driver)
        if not comment_selector:
            print("Selector komentar tidak ditemukan.")
            driver.save_screenshot("debug_screenshot.png")
            return []
        comments = []
        comment_elements = driver.find_elements(By.CSS_SELECTOR, comment_selector)
        print(f"Ditemukan {len(comment_elements)} elemen komentar")
        for i, elem in enumerate(comment_elements):
            try:
                comment_text = elem.text.strip()
                if comment_text and comment_text not in comments:
                    comments.append(comment_text)
                    print(f"Komentar {len(comments)}: {comment_text[:50]}...")
            except (NoSuchElementException, StaleElementReferenceException):
                continue
        print(f"Total komentar diambil: {len(comments)}")
        return analyze_comments_from_data(comments, lexicon)
    except Exception as e:
        print(f"Terjadi error: {e}")
        driver.save_screenshot("error_screenshot.png")
        return []