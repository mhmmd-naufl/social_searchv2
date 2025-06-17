import time
import random
import json
from urllib.parse import quote_plus
from cookies import cookie
from selenium_driver import setup_selenium_driver
from add_cookie import add_cookies_to_driver
# from scrapper_comment import scrappers
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

def search_video(keyword, max_scroll = 4):
    url = f"https://www.tiktok.com/search?q={quote_plus(keyword)}"
    cookies_str = cookie
    enable_scroll = True
    scroll_delay = 3
    css_selector = 'div[data-e2e="search_top-item"]'
    final_result = []
    
    driver = None
    try:
        driver = setup_selenium_driver()
        if cookies_str:
            add_cookies_to_driver(driver, cookies_str)
        print(f"Mengunjungi URL: {url}")
        driver.get(url)

        print(f"Menunggu elemen awal dengan selector: '{css_selector}' muncul...")
        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
            )
            print("Elemen awal ditemukan.")
        except TimeoutException:
            print("Peringatan: Elemen awal tidak ditemukan dalam batas waktu.")

        if enable_scroll:
            print("\nMode scroll diaktifkan. Melakukan scroll untuk memuat konten...")
            last_height = driver.execute_script("return document.body.scrollHeight")
            for i in range(max_scroll):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(scroll_delay + random.uniform(0.5, 2.0)) 

                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print(f"Sudah mencapai bagian bawah halaman setelah {i+1} kali scroll.")
                    break
                last_height = new_height
                print(f"Scroll ke-{i+1} selesai. Tinggi halaman baru: {new_height}px")
            print("Selesai melakukan scroll.")

        elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
        
        if elements:
            for i, element in enumerate(elements):
                try:
                    raw_html = (element.get_attribute('outerHTML'))
                    print(raw_html)
                    try:
                        img_elem = element.find_element(By.CSS_SELECTOR, 'img[alt]')
                        desc = img_elem.get_attribute('alt').strip()
                    except NoSuchElementException:
                        desc = "(desc tidak ditemukan)"

                    # try:
                    #     views_elem = element.find_element(By.CSS_SELECTOR, 'strong[data-e2e="video-views"]')
                    #     views = views_elem.text.strip()
                    # except NoSuchElementException:
                    #     views = "(views tidak ditemukan)"

                    video_links = []
                    authors = []
                    video_ids = []
                    a_tags = element.find_elements(By.CSS_SELECTOR, 'a')
                    for a_tag in a_tags:
                        href = a_tag.get_attribute('href')
                        if href and '/video/' in href:
                            video_links.append(href)
                            try:
                                username = href.split("tiktok.com/@")[1].split("/video/")[0]
                            except Exception:
                                username = "(username tidak ditemukan)"
                            authors.append(username)
                            video_id = href.rstrip('/').split('/')[-1]
                            video_ids.append(video_id)
                            
                    for link in video_links:
                        # comments = scrappers(driver, link, max_comments=10)
                        print(f"Desc   : {desc}")
                        # print(f"Views  : {views}")
                        if authors:
                            for author in authors:
                                print(f"Author  : @{author}")
                        else:
                            print("Author : (tidak ditemukan)")

                        if video_links:
                            for link in video_links:
                                print(f"Link Video : {link}")
                        else:  
                            print("Link Video: (tidak ditemukan)")
                    
                        if video_ids:
                            for vid in video_ids:
                                print(f"ID Video: {vid}")
                        else:
                            print("ID Video: (tidak ditemukan)")
                    
                        print("" + "="*75 + "\n")

                        final_result.append({
                            # "html yang diambil": raw_html,
                            "desc": desc,
                            # "views": views,
                            "authors": authors,
                            "video_links": video_links,
                            "video_id": video_ids,
                            # "comments": comments
                        })
                except Exception as e:
                    print(f"Gagal mengambil detail elemen: {e}")
                    driver.save_screenshot("error_screenshot_detail.png")
                    print("Screenshot error disimpan sebagai 'error_screenshot_detail.png'.")

    except TimeoutException:
        print(f"Timeout: Halaman tidak dimuat atau elemen tidak muncul sama sekali di '{url}' dalam batas waktu.")
    except WebDriverException as e:
        print(f"Kesalahan WebDriver: {e}. Pastikan chromedriver.exe ada di PATH dan versi Chrome Anda kompatibel.")
    except Exception as e:
        print(f"Terjadi kesalahan tak terduga: {e}")
        print(f"Terjadi error: {e}")
        driver.save_screenshot("error_screenshot_page.png")
        print("Screenshot error disimpan sebagai 'error_screenshot_page.png'.")
    
    finally:
        if driver:
            driver.quit()
            
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=4)