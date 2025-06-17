from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time

def scrappers(driver, video_url, max_comments=20):
    driver.get(video_url)
    time.sleep(3)

    comments = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0

    while len(comments) < max_comments and scroll_attempts < 10:
        comment_elements = driver.find_elements(By.CSS_SELECTOR, 'p[data-e2e="comment-level-1"]')
        for elem in comment_elements:
            try:
                span = elem.find_element(By.CSS_SELECTOR, 'span')
                comment_text = span.text.strip()
                
                comment_data = {"comment": comment_text}
                if comment_data not in comments:
                    comments.append(comment_data)
            except NoSuchElementException:
                continue

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scroll_attempts += 1

    return comments[:max_comments]