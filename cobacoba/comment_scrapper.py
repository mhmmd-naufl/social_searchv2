from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def scrape_comments(driver, max_comments=100):
    comments = []
    # Scroll 1x agar komentar termuat
    try:
        comments_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="css-1i7ohvi-DivCommentItemContainer eo72wou0"]'))
        )
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comments_container)
        time.sleep(2 + random.uniform(0.5, 1.5))
    except Exception:
        pass

    comment_elements = driver.find_elements(By.CSS_SELECTOR, 'span[data-e2e="comment-level-1"]')
    print(f"DEBUG: Ditemukan {len(comment_elements)} elemen komentar")
    for idx, elem in enumerate(comment_elements):
        try:
            text = elem.find_element(By.CSS_SELECTOR, 'span')
            print(f"DEBUG: Komentar ke-{idx+1}: {text}")
            comments.append({
                "comment_id": f"comment_{idx}",
                "text": text
            })
            if len(comments) >= max_comments:
                break
        except Exception as e:
            print(f"DEBUG: Gagal mengambil komentar ke-{idx+1}: {e}")
            continue
    print(f"DEBUG: Total komentar yang berhasil diambil: {len(comments)}")
    return comments