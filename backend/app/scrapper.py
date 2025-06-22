import json
import bson
import time
import random
from analysis.analysis_comment import analyze_comments_from_data, lexicon
from urllib.parse import quote_plus
from cookies import cookie
from selenium_driver import setup_selenium_driver
from add_cookie import add_cookies_to_driver
from save import save_to_mongo
from scrapper_comment import cek
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

def search_video(keyword, max_scroll=0):
    url = f"https://www.tiktok.com/search?q={quote_plus(keyword)}"
    cookies_str = cookie
    enable_scroll = True
    scroll_delay = 3
    css_selector = 'div[data-e2e="search_top-item"]'
    video_details = []
    
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
        print(f"Jumlah video ditemukan: {len(elements)}")
        
        if elements:
            for i, element in enumerate(elements):
                try:
                    # raw_html = element.get_attribute('outerHTML')
                    # print(raw_html)
                    try:
                        img_elem = element.find_element(By.CSS_SELECTOR, 'img[alt]')
                        desc = img_elem.get_attribute('alt').strip()
                    except NoSuchElementException:
                        desc = "(desc tidak ditemukan)"

                    video_link = None
                    author = "(username tidak ditemukan)"
                    video_id = "(video_id tidak ditemukan)"
                    a_tags = element.find_elements(By.CSS_SELECTOR, 'a')
                    for a_tag in a_tags:
                        href = a_tag.get_attribute('href')
                        if href and '/video/' in href:
                            video_link = href
                            try:
                                author = href.split("tiktok.com/@")[1].split("/video/")[0]
                            except Exception:
                                author = "(username tidak ditemukan)"
                            video_id = href.rstrip('/').split('/')[-1]
                            break

                    print(f"Desc   : {desc}")
                    print(f"Author : @{author}")
                    print(f"Link Video : {video_link if video_link else '(tidak ditemukan)'}")
                    print(f"ID Video: {video_id}")
                    print(f"keyword: {keyword}")
                    print("" + "="*75 + "\n")

                    data = {
                        "desc": desc,
                        "author": author,
                        "video_link": video_link,
                        "video_id": video_id,
                        "keyword" : keyword
                    }

                    video_details.append(data)
                    
                except Exception as e:
                    print(f"Error mengambil data video ke-{i+1}: {e}")
                    continue

        final_result = []
        for data in video_details:
            try:
                analyzed_comments = cek(driver, data)
                data["comment_analyzed"] = analyzed_comments
                final_result.append(data)
            except Exception as e:
                print(f"Gagal scraping komentar untuk video {data['video_id']}: {e}")

        with open('final_results.json', 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=4)

        for data in final_result:
            save_to_mongo(data)

    except TimeoutException:
        print(f"Timeout: Halaman tidak dimuat atau elemen tidak muncul sama sekali di '{url}' dalam batas waktu.")
    except WebDriverException as e:
        print(f"Kesalahan WebDriver: {e}. Pastikan chromedriver.exe ada di PATH dan versi Chrome Anda kompatibel.")
    except Exception as e:
        print(f"Terjadi kesalahan tak terduga: {e}")
        driver.save_screenshot("error_screenshot_page.png")
        print("Screenshot error disimpan sebagai 'error_screenshot_page.png'.")

    finally:
        try:
            driver.quit()
        except:
            pass

    return final_result
    
if __name__ == "__main__":  
    print("Memulai...")
    search_video("banyuwangi")
    print("\nselesai.")