# Catatan tentang Data Scraping

## Sumber data

Data yang ditampilkan aplikasi berasal dari **komentar publik pada video TikTok**, diambil otomatis dengan Selenium saat fitur scraping dijalankan. Tidak ada login, paywall, atau data privat yang diakses.

## Data pada mode demo / deploy

Aplikasi yang di-deploy memakai **data contoh** dari `backend/demo/sample_videos.json`:
- 12 video, yang sudah memiliki hasil analisis sentimen.
- Data ini adalah **hasil scraping sebelumnya**, bukan hasil real-time.

Alasannya: scraping TikTok di lingkungan cloud sering terkena captcha, halaman login, atau cookie yang kedaluwarsa. Dengan data seed, antarmuka tetap bisa didemonstrasikan tanpa bergantung pada kondisi tersebut.

Banner kecil di halaman hasil akan muncul jika environment variable `VITE_DEMO_MODE=1` aktif.

## Analisis sentimen

- Menggunakan **leksikon buatan sendiri** + Sastrawi, bukan model machine learning supervised.
- Hasilnya bersifat **eksperimen/eduakatif**, bukan ground truth mutlak.
- Kamus KBBI (`indonesian-adjective-sentiment-raw.csv`) tidak memiliki label sentimen, sehingga dipakai hanya sebagai perluasan leksikon opsional (`USE_KBBI_LEXICON=1`).

## Privasi & penggunaan

- Komentar yang tersimpan adalah konten yang sudah publik di platform asal.
- Aplikasi tidak menyimpan informasi pribadi secara sengaja selain username public TikTok.
- Gunakan data ini untuk keperluan belajar/portofolio. Untuk penggunaan komersial, patuhi syarat layanan TikTok dan peraturan perlindungan data yang berlaku.

## Memperbarui data

1. Jalankan scraper di lokal dengan cookie TikTok yang masih valid:
   ```bash
   cd backend
   python -m app.scrapper
   ```
2. Results akan ditulis ke `backend/app/final_results.json`.
3. Salin/sesuaikan ke `backend/demo/sample_videos.json` bila ingin dipakai sebagai data demo.
4. Isi ulang database:
   ```bash
   python seed_demo.py
   ```
5. Deploy ulang Fly/Vercel jika diperlukan.

## Batasan teknis

- Scraper bergantung pada selector `data-e2e` TikTok yang bisa berubah kapan saja.
- Job scraping disimpan in-memory; restart server menghilangkan status job yang belum selesai.
- Untuk kebutuhan produksi, gunakan Redis/Celery, rotasi cookie otomatis, dan penyimpanan data yang sesuai regulasi.
