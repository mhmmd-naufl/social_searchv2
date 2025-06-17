import time
import json

def add_cookies_to_driver(driver, cookies_str):
    if not cookies_str:
        print("Peringatan: `cookies_str` kosong. Melanjutkan tanpa menambahkan cookies.")
        return

    try:
        cookies_list = cookies_str
        driver.get("https://www.tiktok.com/")
        print("Menambahkan cookies...")
        for cookie_dict in cookies_list:
            cookie_to_add = {k: v for k, v in cookie_dict.items() if k in ['name', 'value', 'domain', 'path', 'expiry', 'secure', 'httpOnly']}
            if 'expirationDate' in cookie_dict:
                cookie_to_add['expiry'] = int(cookie_dict['expirationDate'])
            driver.add_cookie(cookie_to_add)
        print("Cookies berhasil ditambahkan. Memuat ulang halaman.")
        driver.get("https://www.tiktok.com/")
        time.sleep(3)
    except json.JSONDecodeError:
        print("Error: `cookies_str` bukan JSON yang valid. Pastikan formatnya benar.")
    except Exception as e:
        print(f"Peringatan: Gagal menambahkan cookies. Error: {e}")