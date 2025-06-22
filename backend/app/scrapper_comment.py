import time
import random
import json
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

# def simulate_human_mouse_movement(driver):
#     actions = ActionChains(driver)
#     window_size = driver.get_window_size()
#     x = random.randint(0, window_size['width'] - 1)
#     y = random.randint(0, window_size['height'] - 1)
#     actions.move_by_offset(x, y).perform()
#     time.sleep(random.uniform(0.5, 1.5))

def human_like_scroll(driver):
    scroll_heights = [200, 300, 400, 500]
    for _ in range(random.randint(2, 5)):
        scroll_height = random.choice(scroll_heights)
        driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(random.uniform(1, 3))
    return driver.execute_script("return document.body.scrollHeight")

def random_delay(min_delay=1, max_delay=3):
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

def simulate_reading_behavior(driver):
    reading_time = random.uniform(2, 8)
    time.sleep(reading_time)
    if random.random() < 0.4:
        driver.execute_script("window.scrollBy(0, 100);")
        time.sleep(random.uniform(1, 2))

def wait_for_page_load(driver):
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(3)

def find_comment_selectors(driver):
    possible_selectors = [
        'span[data-e2e="comment-level-1"]'
    ]
    for selector in possible_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"Ditemukan {len(elements)} elemen dengan selector: {selector}")
                return selector
        except:
            continue
    return None

def scroll_to_comments_section(driver):
    try:
        comment_selectors = [
            'span[data-e2e="comment-level-1"]'
        ]
        for selector in comment_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(2)
                if element.tag_name == 'button':
                    element.click()
                    time.sleep(3)
                break
            except:
                continue
    except Exception as e:
        print(f"Gagal scroll ke komentar: {e}")

def cek(driver, video_data):
    try:
        url = video_data["video_link"]
        driver.get(url)
        random_delay(2, 4)
        print(f"Mengunjungi URL: {url}")
        wait_for_page_load(driver)
        simulate_reading_behavior(driver)
        # simulate_human_mouse_movement(driver)
        scroll_to_comments_section(driver)
        human_like_scroll(driver)
        page_source = driver.page_source
        if "comment" in page_source.lower():
            print("Kata 'comment' ditemukan di halaman")
        else:
            print("Kata 'comment' TIDAK ditemukan di halaman")
        comment_selector = find_comment_selectors(driver)
        if not comment_selector:
            time.sleep(12)
            comment_selector = find_comment_selectors(driver)
        if not comment_selector:
            print("Masih tidak ditemukan selector komentar. Mengambil screenshot...")
            driver.save_screenshot("debug_screenshot.png")
            print("=== Page Source (first 3000 chars) ===")
            print(driver.page_source[:3000])
            return []
        comments = []
        scroll_attempts = 0
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_to_comments_section(driver)
        while len(comments) < 30 and scroll_attempts < 15:
            try:
                comment_elements = driver.find_elements(By.CSS_SELECTOR, comment_selector)
                print(f"Ditemukan {len(comment_elements)} elemen komentar")
                for i, elem in enumerate(comment_elements):
                    try:
                        comment_text = None
                        text_selectors = [
                            'p[class="TUXText TUXText--tiktok-sans css-1658qcl-StyledTUXText e1vx58lt0"]',
                        ]
                        for text_sel in text_selectors:
                            try:
                                text_elem = elem.find_element(By.CSS_SELECTOR, text_sel)
                                comment_text = text_elem.text.strip()
                                if comment_text:
                                    break
                            except:
                                continue
                        if not comment_text:
                            comment_text = elem.text.strip()
                        if comment_text and len(comment_text) > 0:
                            if not any(c == comment_text for c in comments):
                                comments.append(comment_text)
                                print(f"Komentar {len(comments)}: {comment_text[:50]}...")
                    except (NoSuchElementException, StaleElementReferenceException) as e:
                        print(f"Error mengambil komentar {i}: {e}")
                        continue
            except StaleElementReferenceException:
                print("Stale element, retry...")
                continue
            print(f"Scroll attempt {scroll_attempts + 1}")
            driver.execute_script("window.scrollBy(0, 500);")
            random_delay(2, 4)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Tidak ada konten baru setelah scroll")
                break
            last_height = new_height
            scroll_attempts += 1
        print(f"\n=== HASIL ===")
        print(f"Total komentar diambil: {len(comments)}")
        return comments
    except Exception as e:
        print(f"Terjadi error: {e}")
        driver.save_screenshot("error_screenshot.png")
        print("Screenshot error disimpan")
        return []