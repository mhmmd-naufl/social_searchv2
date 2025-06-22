from selenium.webdriver.common.by import By

def scrape_video_detail(driver):
    try:
        desc = driver.find_element(By.XPATH, "//h1[@data-e2e='video-desc']").text.strip()
    except:
        desc = ""
    try:
        author = driver.find_element(By.XPATH, "//a[@data-e2e='video-author-uniqueid']").text.strip()
    except:
        author = ""
    video_link = driver.current_url
    video_id = ""
    import re
    match = re.search(r'/video/(\d+)', video_link)
    if match:
        video_id = match.group(1)
    return {
        "desc": desc,
        "author": author,
        "video_link": video_link,
        "video_id": video_id
    }