# Panduan Deploy Lengkap

Stack: **Vercel** (frontend React) + **Fly.io** (API FastAPI) + **MongoDB Atlas** (database).

> Urutan penting: Atlas → seed data → Fly.io → Vercel → set CORS di Fly.
> Jangan lakukan Vercel lebih dulu, karena Anda butuh URL API untuk `VITE_API_URL`.

---

## 0. Prasyarat

- Akun GitHub (repo sudah ada di `https://github.com/mhmmd-naufl/social_searchv2`).
- Akun [MongoDB Atlas](https://www.mongodb.com/atlas) (gratis).
- Akun [Fly.io](https://fly.io) + `flyctl` terinstall.
- Akun [Vercel](https://vercel.com) (bisa login dengan GitHub).
- Python 3.10+ dan Node 18+ di lokal (untuk seed data).

Install `flyctl` di Windows (PowerShell):

```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

Tutup & buka PowerShell baru, lalu cek:

```powershell
fly version
```

---

## 1. MongoDB Atlas

1. Buka https://www.mongodb.com/atlas → **Sign In** / **Register**.
2. Klik **Create a project** → kasih nama mis. `social-search`, klik **Create**.
3. Klik **Create a Database Deployments** → pilih **Shared (M0)** → **Create**.
   - Provider/region: pilih yang dekat (mis. Singapore / Asia Pacific).
   - Cluster name: bebas, mis. `Cluster0`.
   - Klik **Create Deployment**. Tunggu 1–3 menit sampai status hijau.

4. **Buat user database**
   - Menu kiri **Database Access** → **Add New Database User**.
   - Authentication: **Password**.
   - Isi username & password (simpan dulu!). Role: **Read and write to any database**.
   - Klik **Add User**.

5. **Izinkan IP public**
   - Menu kiri **Network Access** → **Add IP Address**.
   - Pilih **Allow Access from Anywhere** (`0.0.0.0/0`).
   - Klik **Confirm**. (Ini perlu karena Fly.io tidak punya IP statis tetap di tier dasar.)

6. **Ambil connection string**
   - Klik **Connect** pada cluster → **Connect your application**.
   - Driver: **Python**, version: **3.12 atau yang terdekat**.
   - Salin string seperti:
     ```
     mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
     ```
   - Ganti `USERNAME` dan `PASSWORD` dengan user dari langkah 4.

---

## 2. Seed data demo (wajib)

Tanpa langkah ini, halaman hasil akan kosong karena scraping di cloud tidak dijamin berhasil.

Dari folder proyek:

```powershell
cd backend
$env:MONGO_URI="mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
python seed_demo.py
```

Output yang diharapkan:

```
Seed selesai: 12 dokumen ditulis. Total: 12
```

Kalau error:
- `ServerSelectionTimeoutError` → cek Network Access Atlas (`0.0.0.0/0`) dan password (jangan ada karakter `@` belum di-encode; gunakan URL-encode jika perlu).
- `ModuleNotFoundError` → jalankan `pip install pymongo python-dotenv`.

---

## 3. Deploy API ke Fly.io

1. Login:
   ```powershell
   fly auth login
   ```
   Browser akan terbuka untuk login.

2. **Edit `fly.toml`** di root repo. Baris pertama:
   ```toml
   app = "social-search-api"
   ```
   Ganti dengan nama unik secara global, misal:
   ```toml
   app = "social-search-naufal-2026"
   ```
   Kalau nama sudah dipakai orang lain, `fly deploy` akan error — ganti lagi.

3. Set secret (jangan pernah ditaruh di `fly.toml`):
   ```powershell
   fly secrets set MONGO_URI="mongodb+srv://USERNAME:PASSWORD@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
   ```

4. Deploy dari **root repository**:
   ```powershell
   fly deploy
   ```
   Fly akan membangun image dari `Dockerfile.fly` (butuh beberapa menit pertama kali).

5. Verifikasi:
   ```powershell
   fly open
   ```
   atau buka `https://<nama-app>.fly.dev/docs`. Harus muncul halaman Swagger.
   Cek juga:
   ```powershell
   fly logs
   ```
   Tidak boleh ada error koneksi Mongo.

6. Catat URL API Anda: `https://<nama-app>.fly.dev`

---

## 4. Deploy frontend ke Vercel

1. Buka https://vercel.com → **Add New... → Project**.
2. Klik **Import** pada repository `mhmmd-naufl/social_searchv2`.
3. Saat konfigurasi project:
   - **Project Name**: bebas.
   - **Framework Preset**: Vite (terdeteksi otomatis).
   - **Root Directory**: klik **Edit** → pilih `frontend` → **Continue**.
   - **Build Command**: `npm run build` (default).
   - **Output Directory**: `dist` (default).
4. Sebelum klik Deploy, buka bagian **Environment Variables**:
   - Name: `VITE_API_URL`
   - Value: `https://<nama-app>.fly.dev` (dari langkah 3)
   - Centang **Production**, **Preview**, **Development**.
   - Tambah juga jika ingin banner demo muncul:
     - Name: `VITE_DEMO_MODE`
     - Value: `1`
5. Klik **Deploy**. Tunggu selesai (1–3 menit).
6. Buka URL Vercel, misal `https://social-search-xxx.vercel.app`.
   Halaman home harus tampil.

---

## 5. Set CORS di Fly (langkah terakhir)

API belum mengizinkan domain Vercel sebelum ini dilakukan.

```powershell
fly secrets set CORS_ORIGINS="https://social-search-xxx.vercel.app"
```

Fly akan me-restart machine otomatis. Tunggu sampai `fly logs` menunjukkan aplikasi siap.

Kalau ingin mengizinkan beberapa origin (mis. production + preview):

```powershell
fly secrets set CORS_ORIGINS="https://social-search-xxx.vercel.app,https://social-search-git-main-xxx.vercel.app"
```

---

## 6. Verifikasi akhir

| Cek | Cara | Harapan |
|---|---|---|
| API hidup | Buka `https://<nama-app>.fly.dev/docs` | Swagger muncul |
| Database terisi | `fly ssh console` lalu mongo shell, atau lihat di Atlas Collections | 12 dokumen |
| Web tampil | Buka URL Vercel | Halaman home desain baru |
| Pencarian jalan | Ketik `banyuwangi` → Cari | 12 kartu hasil muncul |
| Detail jalan | Klik "Lihat analisis lengkap" | Donut chart + komentar |
| Tanpa error CORS | Buka DevTools → Console di Vercel | Tidak ada merah "blocked by CORS" |

---

## 7. Update setelah deploy

### Update kode
```powershell
git add -A
git commit -m "update"
git push origin main
```
- Vercel auto-deploy dari GitHub.
- Fly tidak auto-deploy — jalankan manual: `fly deploy`.

### Update data saja
```powershell
cd backend
$env:MONGO_URI="mongodb+srv://..."; python seed_demo.py
```
Tidak perlu deploy ulang, cukup refresh halaman.

### Ganti secret
```powershell
fly secrets set MONGO_URI="string baru"
fly secrets set CORS_ORIGINS="https://domain-baru.vercel.app"
```

---

## 8. Troubleshooting

| Gejala | Penyebab | Solusi |
|---|---|---|
| Hasil kosong | Database belum di-seed | Jalankan `python seed_demo.py` |
| Error CORS di browser | `CORS_ORIGINS` belum/salah | `fly secrets set CORS_ORIGINS="https://xxx.vercel.app"` (tanpa `/` di akhir) |
| `ServerSelectionTimeoutError` | IP Atlas belum diizinkan / password salah | Network Access `0.0.0.0/0`, cek user |
| 404 saat refresh `/hasil` | Routing SPA belum benar | Pastikan `frontend/vercel.json` ikut ter-deploy |
| `VITE_API_URL` tidak terbaca | Env di-set setelah build | Set env Vercel lalu **Redeploy** |
| Fly deploy gagal "app name taken" | Nama app sudah dipakai | Ganti `app = "..."` di `fly.toml` |
| Web lelet saat buka pertama | Machine Fly cold start / sleep | `min_machines_running = 1` di `fly.toml` (cek kuota) |
| Scraping gagal | Cookie expired / captcha | Normal di cloud; pakai data seed untuk demo, jalankan scraper di lokal untuk data baru |

---

## 9. Catatan biaya

- Atlas M0: gratis.
- Vercel Hobby: gratis untuk personal.
- Fly.io: **tidak sepenuhnya gratis**. Konfigurasi `min_machines_running = 1` menjaga API tetap hidup tapi bisa menimbulkan biaya kecil. Cek dashboard Fly → **Billing** sebelum mengaktifkan. Jika ingin hemat, set `min_machines_running = 0` dan terima cold start saat demo.

---

## 10. Link penting

- Repo: https://github.com/mhmmd-naufl/social_searchv2
- Catatan data: [DATA_NOTICE.md](DATA_NOTICE.md)
- API docs: `https://<nama-app>.fly.dev/docs`
