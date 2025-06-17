import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
import random
import json
from add_cookie import add_cookies_to_driver
from cookies import cookie as cookies_str
from selenium_driver import setup_selenium_driver

def simulate_human_mouse_movement(driver):
    actions = ActionChains(driver)
    x = random.randint(100, 800)
    y = random.randint(100, 600)
    actions.move_by_offset(x, y).perform()
    time.sleep(random.uniform(0.5, 1.5))

def human_like_scroll(driver):
    # Scroll dengan kecepatan dan jarak yang bervariasi
    scroll_heights = [200, 300, 400, 500]
    for _ in range(random.randint(2, 5)):
        scroll_height = random.choice(scroll_heights)
        driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        time.sleep(random.uniform(1, 3))
        
        # Kadang scroll ke atas sedikit (seperti manusia)
        if random.random() < 0.3:
            driver.execute_script("window.scrollBy(0, -50);")
            time.sleep(random.uniform(0.5, 1))
    
    # Return current scroll height
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
    """Tunggu halaman fully loaded"""
    WebDriverWait(driver, 30).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(3)  # Extra wait untuk dynamic content

def find_comment_selectors(driver):
    """Cari selector komentar yang tepat"""
    possible_selectors = [
        'div[data-e2e="comment-item"]',
        'div[class*="comment"]',
        'div[class*="Comment"]',
        '[data-e2e*="comment"]',
        'div[class*="DivCommentItemContainer"]',
        'div[class*="comment-item"]',
        'div[class="css-7whb78-DivCommentListContainer ezgpko40"]'
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
    """Scroll ke bagian komentar"""
    try:
        # Cari bagian komentar atau tombol komentar
        comment_selectors = [
            'button[data-e2e="browse-comment"]',
            'button[data-e2e="comment-icon"]',
            'div[data-e2e="comment-list"]',
            '[class*="comment"]',
            'span[data-e2e="comment-level-1"]'
        ]
        
        for selector in comment_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                time.sleep(2)
                # Jika ada tombol, klik
                if element.tag_name == 'button':
                    element.click()
                    time.sleep(3)
                break
            except:
                continue
    except Exception as e:
        print(f"Gagal scroll ke komentar: {e}")

def cek():
    driver = setup_selenium_driver()
    try:
        url = "https://www.tiktok.com/@poppyfara/video/7450756249769020677"
        
        random_delay(2, 4)
        
        if cookies_str:
            add_cookies_to_driver(driver, cookies_str)
        
        print(f"Mengunjungi URL: {url}")
        driver.get(url)
        
        # Tunggu halaman fully loaded
        wait_for_page_load(driver)
        
        # Simulasi perilaku manusia setelah load
        simulate_reading_behavior(driver)
        simulate_human_mouse_movement(driver)
        
        # Scroll ke bagian komentar
        scroll_to_comments_section(driver)
        
        # Scroll dengan perilaku manusia
        human_like_scroll(driver)
        
        # Debug: Print page source snippet untuk melihat struktur
        print("=== DEBUG: Mencari struktur halaman ===")
        page_source = driver.page_source
        if "comment" in page_source.lower():
            print("Kata 'comment' ditemukan di halaman")
        else:
            print("Kata 'comment' TIDAK ditemukan di halaman")
        
        # Cari selector yang tepat
        comment_selector = find_comment_selectors(driver)
        
        if not comment_selector:
            print("Tidak ada selector komentar yang ditemukan!")
            # Coba tunggu lebih lama
            print("Menunggu 10 detik tambahan...")
            time.sleep(10)
            comment_selector = find_comment_selectors(driver)
        
        if not comment_selector:
            print("Masih tidak ditemukan selector komentar. Mengambil screenshot...")
            driver.save_screenshot("debug_screenshot.png")
            # Print sebagian page source untuk debug
            print("=== Page Source (first 3000 chars) ===")
            print(driver.page_source[:3000])
            return
          
        comments = []
        scroll_attempts = 0
        last_height = driver.execute_script("return document.body.scrollHeight")

        while len(comments) < 20 and scroll_attempts < 10:
            try:
                comment_elements = driver.find_elements(By.CSS_SELECTOR, comment_selector)
                print(f"Ditemukan {len(comment_elements)} elemen komentar")
                
                for i, elem in enumerate(comment_elements):
                    try:
                        # Coba berbagai selector untuk teks komentar
                        comment_text = None
                        text_selectors = [
                            'p[data-e2e="comment-level-1"]',
                            'span[data-e2e="comment-level-1"]',
                            'p',
                            'span',
                            '[class*="comment-text"]'
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
                            comment_data = {
                                "comment": comment_text,
                                "index": len(comments) + 1
                            }
                            
                            # Cek duplikasi
                            if not any(c["comment"] == comment_text for c in comments):
                                comments.append(comment_data)
                                print(f"Komentar {len(comments)}: {comment_text[:50]}...")
                                
                    except (NoSuchElementException, StaleElementReferenceException) as e:
                        print(f"Error mengambil komentar {i}: {e}")
                        continue
                        
            except StaleElementReferenceException:
                print("Stale element, retry...")
                continue

            # Scroll untuk load komentar lebih banyak
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
        
        if comments:
            for c in comments:
                print(f"{c['index']}: {c['comment']}")

            # Simpan ke file JSON
            with open("comments_result.json", "w", encoding="utf-8") as f:
                json.dump(comments, f, ensure_ascii=False, indent=2)
            print(f"Komentar disimpan ke comments_result.json")
        else:
            print("Tidak ada komentar yang berhasil diambil")

    except Exception as e:
        print(f"Terjadi error: {e}")
        driver.save_screenshot("error_screenshot.png")
        print("Screenshot error disimpan")

    finally:
        driver.quit()

if __name__ == "__main__":
    print("Memulai scraping komentar TikTok...")
    cek()
    print("Selesai.")
