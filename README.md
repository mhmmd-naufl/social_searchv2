# Social Search

Aplikasi untuk mencari konten TikTok berdasarkan kata kunci, mengambil komentar,
lalu menganalisis sentimennya (positif / negatif / netral). Dibuat sebagai
proyek magang semester.

## Fitur

- Pencarian video TikTok via Selenium, dengan beberapa selector cadangan.
- Scroll otomatis pada halaman hasil dan pada daftar komentar.
- Analisis sentimen berbasis leksikon bahasa Indonesia + normalisasi slang,
  negasi, bigram, dan emoji.
- Penyimpanan hasil ke MongoDB dengan **upsert** (tidak menumpuk duplikat).
- Proses scraping dijalankan sebagai **job background**; frontend melakukan
  polling agar tidak menunggu HTTP request berlama-lama.
- UI React: halaman pencarian, daftar hasil dengan ringkasan sentimen, dan
  halaman detail dengan grafik pie serta filter komentar.
- Endpoint cuaca melalui proxy backend (API key tidak terekspos ke browser).

## Tech stack

| Layer | Teknologi |
|---|---|
| Frontend | React 19, Vite 6, React Router 7, Chart.js |
| Backend | FastAPI, Uvicorn, Selenium, PyMongo |
| Database | MongoDB |
| Analisis | NLTK stopwords, Sastrawi stemmer, leksikon buatan sendiri |
| Deployment | Docker Compose |

## Struktur folder

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # endpoint FastAPI
│   │   ├── config.py            # semua konfigurasi dari env
│   │   ├── database.py          # koneksi Mongo singleton
│   │   ├── jobs.py              # penyimpanan job background
│   │   ├── scrapper.py          # scraping halaman pencarian
│   │   ├── scrapper_comment.py  # scraping komentar
│   │   ├── save.py              # upsert ke MongoDB
│   │   ├── selenium_driver.py   # inisialisasi browser
│   │   ├── cookies.py           # loader cookie (bukan hardcode)
│   │   └── analysis/            # leksikon, preprocessing, builder KBBI
│   ├── tests/
│   ├── requirements.txt
│   └── requirements-dev.txt
├── frontend/src/
│   ├── App.jsx      # halaman pencarian
│   ├── Hasil.jsx    # hasil + polling job
│   └── Detail.jsx   # detail video + grafik
├── docker-compose.yml
└── indonesian-adjective-sentiment-raw.csv   # kamus KBBI (tanpa label sentimen)
```

## Menjalankan secara lokal

### 1. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements-dev.txt
python -m nltk.downloader stopwords

copy .env.example .env          # lalu isi nilainya
cd ..
uvicorn app.main:app --reload --app-dir backend --port 8000
```

Pastikan MongoDB berjalan di `localhost:27017`, chromedriver tersedia, dan
cookie TikTok diletakkan di `backend/app/cookies.json` (atau di env
`TIKTOK_COOKIES_JSON`).

### 2. Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Buka `http://localhost:5173`.

### 3. Menjalankan tes

```bash
cd backend
python -m pytest
```

## Menjalankan dengan Docker

```bash
copy .env.example .env   # opsional: isi OPENWEATHER_API_KEY dll.
docker compose up --build
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000/docs`
- MongoDB: `localhost:27017`

## Konfigurasi (environment)

| Variable | Default | Keterangan |
|---|---|---|
| `MONGO_URI` | `mongodb://localhost:27017` | Alamat MongoDB |
| `DB_NAME` | `new_tiktok_db` | Nama database |
| `COLLECTION_NAME` | `videos` | Nama koleksi |
| `CORS_ORIGINS` | `http://localhost:5173` | Origin frontend yang diizinkan |
| `OPENWEATHER_API_KEY` | kosong | API key cuaca (di backend saja) |
| `OPENWEATHER_CITY` | `Banyuwangi` | Kota cuaca |
| `TIKTOK_COOKIES_JSON` | kosong | Cookie TikTok berupa JSON array |
| `TIKTOK_COOKIES_FILE` | `backend/app/cookies.json` | Path file cookie lokal |
| `USE_KBBI_LEXICON` | `0` | `1` untuk memakai leksikon tambahan dari KBBI |
| `CHROMEDRIVER_PATH` | otomatis | Path chromedriver |
| `BROWSER_BINARY` | otomatis | Path browser (Brave/Chromium) |
| `HEADLESS` | `0` | `1` untuk mode headless |
| `VITE_API_URL` | `http://localhost:8000` | Base URL API (frontend) |

## API endpoint

| Method | Endpoint | Deskripsi |
|---|---|---|
| `GET` | `/` | Health check sederhana |
| `GET` | `/weather?city=...` | Suhu saat ini (proxy OpenWeatherMap) |
| `POST` | `/search?keyword=...` | Mulai job scraping, mengembalikan `job_id` |
| `GET` | `/search/status/{job_id}` | Cek status job (`pending`/`running`/`done`/`failed`) |
| `GET` | `/search?keyword=...` | Endpoint lama (blocking, kompatibilitas) |
| `GET` | `/video?video_id=...` | Ambil detail satu video |

## Cara kerja analisis sentimen

1. Teks lowercase, emoji dipisahkan dan dipertahankan.
2. Normalisasi slang (`gak` → `tidak`, `bgt` → `sangat`, dll.).
3. Stopword dibuang, kata di-stem dengan Sastrawi. Kata negasi tetap disimpan.
4. Skor dihitung dari leksikon, termasuk bigram (`luar biasa`, `sakit hati`).
5. Kata negasi membalik skor token berikutnya dalam jendela 3 kata, sehingga
   `"tidak suka"` berubah dari positif menjadi negatif.
6. Skor > 0 → `positif`, < 0 → `negatif`, selebihnya → `netral`.

File `indonesian-adjective-sentiment-raw.csv` adalah kamus KBBI **tanpa label
sentimen**. Karena itu tidak bisa dipakai untuk training model supervised.
Skrip `lexicon_builder.py` menggunakan definisinya untuk membangun leksikon
tambahan (`lexicon_kbbi.json`) yang bisa diaktifkan dengan `USE_KBBI_LEXICON=1`.
Untuk perbandingan dengan model ML, dibutuhkan dataset komentar berlabel yang
belum tersedia di repository ini.

## Catatan penting

- Cookie TikTok bersifat sensitif dan cepat kedaluwarsa. Jangan pernah
  meng-commit cookie atau API key. Keduanya sudah masuk ke `.gitignore`.
- Riwayat git lama masih mengandung secret dari versi awal. Sebelum
  mempublikasikan repository, lakukan rotasi kredensial dan pertimbangkan
  `git filter-repo` untuk membersihkan history.
- Scraping TikTok rentan berubah kapan saja (selector, captcha, login).
  Aplikasi sudah punya fallback selector, tetapi tetap perlu pemeliharaan.
- Job scraping disimpan in-memory. Data job hilang saat server restart;
  gunakan Redis/Celery jika dibutuhkan untuk produksi.

## Status

Proyek magang — dikembangkan bertahap:
- Fase 1: keamanan kredensial, CORS, stabilitas dasar, upsert MongoDB.
- Fase 2: fallback selector, scroll komentar, job background, perbaikan sentimen.
- Fase 3: Docker, dokumentasi, unit test, CI.
