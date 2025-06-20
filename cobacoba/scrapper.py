import time
import random
import json
import re # Tambahkan import re untuk regex
from urllib.parse import quote_plus
from cookies import cookie
from selenium_driver import setup_selenium_driver
from add_cookie import add_cookies_to_driver
from save import save_to_mongo # Tetap pakai jika Anda masih ingin menyimpan per video ke MongoDB
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# Import modul baru kita
from sentiment_analyzer import SentimentAnalyzer
from data_processor import DataProcessor

def scrape_and_analyze_tiktok(keyword, num_videos_to_scrape=6):
    url = f"https://www.tiktok.com/search?q={quote_plus(keyword)}"
    cookies_str = cookie
    output_json_filename = "tiktok_search_comments_with_sentiment.json"
    
    # Inisialisasi Analyzer dan Data Processor
    sentiment_analyzer = SentimentAnalyzer()
    data_processor = DataProcessor()

    driver = None
    try:
        driver = setup_selenium_driver()
        if cookies_str:
            add_cookies_to_driver(driver, cookies_str)
        print(f"Mengunjungi URL pencarian: {url}")
        driver.get(url)

        # Tunggu sampai elemen hasil pencarian muncul (tidak usah scroll di sini)
        # XPath ini SANGAT MUNGKIN perlu disesuaikan jika struktur HTML TikTok berubah
        # Ini mencari div yang berisi link video pertama di hasil pencarian
        first_video_card_xpath = "//div[@data-e2e='search_top-item']//a[contains(@href, '/video/')]"
        
        print(f"Menunggu video pertama di hasil pencarian muncul...")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, first_video_card_xpath))
            )
            print("Video pertama ditemukan di hasil pencarian.")
        except TimeoutException:
            print("Peringatan: Video pertama tidak ditemukan dalam batas waktu. Mungkin tidak ada hasil atau struktur HTML berubah.")
            return [] # Keluar jika tidak ada video

        # Ambil semua elemen video yang terlihat di halaman pertama (tanpa scroll)
        # Perhatikan: ini akan mengambil video dari kategori "Top" atau yang pertama muncul
        video_elements_on_search_page_xpath = "//div[@data-e2e='search_top-item']"
        
        # Pastikan elemen sudah dimuat sebelum mencari semua
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, video_elements_on_search_page_xpath))
        )
        elements_to_click = driver.find_elements(By.XPATH, video_elements_on_search_page_xpath)
        
        if not elements_to_click:
            print("Tidak ada elemen video yang dapat diklik di halaman pencarian.")
            return []

        print(f"Ditemukan {len(elements_to_click)} video di halaman pencarian awal.")

        scraped_video_count = 0
        current_video_idx = 0 # Indeks untuk video yang akan diklik dari daftar di halaman pencarian
        
        while scraped_video_count < num_videos_to_scrape and current_video_idx < len(elements_to_click):
            print(f"\n--- Memproses Video ke-{scraped_video_count + 1} ---")
            
            # Re-find element to avoid StaleElementReferenceException
            try:
                # Mengklik elemen video dari hasil pencarian (berdasarkan indeks)
                # Pastikan elemen masih ada dan bisa diklik
                target_video_link = elements_to_click[current_video_idx].get_attribute('href')
                print(f"Mengklik link video: {target_video_link}")
                driver.get(target_video_link) # Langsung navigasi ke link video untuk menghindari klik error
                time.sleep(5) # Beri waktu halaman video untuk memuat

                # Periksa apakah URL berubah, menandakan navigasi berhasil
                if "/video/" not in driver.current_url:
                    print("Navigasi ke halaman video gagal atau URL tidak sesuai. Mencoba video selanjutnya.")
                    current_video_idx += 1
                    continue

            except (NoSuchElementException, TimeoutException, WebDriverException) as e:
                print(f"Gagal mengklik/menavigasi video pada indeks {current_video_idx}: {e}. Mencoba video selanjutnya.")
                current_video_idx += 1
                continue
            
            # Ambil detail video (desc, author, link, id, keyword)
            current_video_data = {}
            current_video_data["keyword"] = keyword
            current_video_data["video_link"] = driver.current_url
            
            match = re.search(r'/video/(\d+)', driver.current_url)
            if match:
                current_video_data["video_id"] = match.group(1)
            else:
                current_video_data["video_id"] = "(video_id tidak ditemukan)"
            
            try:
                # Ambil desc dan author dari elemen di halaman video
                desc_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//h1[@data-e2e='video-desc']"))
                )
                current_video_data["desc"] = desc_element.text.strip()
            except TimeoutException:
                current_video_data["desc"] = "(desc tidak ditemukan di halaman video)"

            try:
                author_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//a[@data-e2e='video-author-uniqueid']"))
                )
                current_video_data["author"] = author_element.text.strip()
            except TimeoutException:
                current_video_data["author"] = "(username tidak ditemukan di halaman video)"

            print(f"Video ID: {current_video_data['video_id']}")
            print(f"Desc: {current_video_data['desc']}")
            print(f"Author: @{current_video_data['author']}")

            # Scrape Komentar (1 scroll)
            print("Memulai scraping komentar...")
            comments_data = []
            
            # Gulir 1 kali untuk memuat komentar awal
            # XPath untuk kontainer komentar:
            comments_container_xpath = "//div[@data-e2e='comment-container']" 
            
            try:
                comments_container = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, comments_container_xpath))
                )
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", comments_container)
                time.sleep(2 + random.uniform(0.5, 1.5)) # Beri waktu untuk memuat komentar setelah scroll
                print("Melakukan 1 kali scroll komentar.")
            except Exception as e:
                print(f"Tidak dapat menemukan kontainer komentar atau melakukan scroll: {e}")
            
            # Cari semua elemen komentar yang terlihat
            comment_elements_xpath = "//div[@data-e2e='comment-container']//div[@data-e2e='comment-item']"
            
            try:
                # Tunggu hingga beberapa komentar muncul
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, comment_elements_xpath))
                )
                comment_elements = driver.find_elements(By.XPATH, comment_elements_xpath)
                
                if not comment_elements:
                    print("Tidak ada komentar ditemukan pada halaman ini.")
                
                for idx, comment_element in enumerate(comment_elements):
                    try:
                        comment_text_xpath = ".//p[@data-e2e='comment-content']"
                        comment_text = comment_element.find_element(By.XPATH, comment_text_xpath).text
                        
                        comments_data.append({
                            'comment_id': f"comment_{idx}_{current_video_data['video_id']}",
                            'text': comment_text
                        })
                    except NoSuchElementException:
                        print(f"Peringatan: Teks komentar tidak ditemukan untuk elemen komentar ke-{idx}.")
                        continue
                    except Exception as e:
                        print(f"Gagal mengambil detail komentar ke-{idx}: {e}")
                        continue
                
                print(f"Berhasil mengambil {len(comments_data)} komentar dari video ini.")

                # Analisis Sentimen dan Gabungkan Data
                processed_comments = []
                for comment in comments_data:
                    sentiment = sentiment_analyzer.analyze_sentiment(comment['text'])
                    processed_comments.append({
                        'comment_id': comment['comment_id'],
                        'text': comment['text'],
                        'sentiment': sentiment
                    })
                
                data_processor.add_video_comments_with_sentiment(current_video_data, processed_comments)
                scraped_video_count += 1
                
            except TimeoutException:
                print("Tidak ada komentar yang muncul dalam batas waktu yang ditentukan.")
            except Exception as e:
                print(f"Terjadi kesalahan saat mencoba mengambil komentar: {e}")

            # Navigasi ke Video Selanjutnya (klik panah bawah)
            if scraped_video_count < num_videos_to_scrape:
                try:
                    # XPath untuk tombol panah bawah (seringkali data-e2e='arrow-right' atau sejenisnya)
                    next_button_xpath = "//button[@data-e2e='arrow-right']" 
                    
                    next_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, next_button_xpath))
                    )
                    
                    print("Mengklik tombol panah bawah untuk video selanjutnya...")
                    next_button.click()
                    time.sleep(5 + random.uniform(0.5, 2.0)) # Beri waktu halaman video baru untuk memuat
                    current_video_idx += 1 # Pindah ke indeks selanjutnya untuk potensi video berikutnya
                except TimeoutException:
                    print("Tombol panah bawah tidak ditemukan atau tidak bisa diklik dalam batas waktu. Mungkin sudah video terakhir atau elemen berubah.")
                    break # Keluar dari loop jika tidak bisa ke video selanjutnya
                except Exception as e:
                    print(f"Terjadi kesalahan saat mengklik tombol panah bawah: {e}")
                    break
            else:
                print(f"Jumlah video yang diminta ({num_videos_to_scrape}) sudah tercapai.")
                break

    except TimeoutException:
        print(f"Timeout: Halaman tidak dimuat atau elemen tidak muncul sama sekali di '{url}' dalam batas waktu.")
    except WebDriverException as e:
        print(f"Kesalahan WebDriver: {e}. Pastikan chromedriver.exe ada di PATH dan versi Chrome Anda kompatibel.")
    except Exception as e:
        print(f"Terjadi kesalahan tak terduga: {e}")
        if driver:
            driver.save_screenshot("error_screenshot_page.png")
            print("Screenshot error disimpan sebagai 'error_screenshot_page.png'.")
        
    finally:
        if driver:
            driver.quit()
        
        # Simpan semua data yang terkumpul ke JSON di akhir
        data_processor.save_to_json(output_json_filename)
        print(f"\nProses selesai. Data tersimpan di {output_json_filename}")
    
    return data_processor.get_data() # Kembalikan data yang sudah diproses

if __name__ == "__main__":  
    print("Memulai proses scraping dan analisis sentimen...")
    # Anda bisa meminta input keyword dan jumlah video dari user
    search_keyword = input("Masukkan keyword pencarian (misal: banyuwangi): ")
    num_videos = int(input("Berapa video yang ingin di-scrape komentarnya? (disarankan 6-9): "))
    
    # Panggil fungsi utama
    scraped_data = scrape_and_analyze_tiktok(search_keyword, num_videos)
    # Anda bisa mencetak sebagian data jika diperlukan untuk verifikasi
    # print(json.dumps(scraped_data[:2], indent=4, ensure_ascii=False)) # Cetak 2 entri pertama
    print("\nProses selesai sepenuhnya.")