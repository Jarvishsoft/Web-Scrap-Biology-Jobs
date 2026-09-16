# 🔬 Web Scraper Lowongan Kerja Biologi Fresh Graduate (Jabek: Jakarta - Bekasi)

Repositori ini adalah alat otomasi berbasis **Python** untuk mencari, mengumpulkan (*scraping*), menyaring, dan menyajikan data lowongan pekerjaan terkini di Indonesia, khususnya wilayah **Jakarta dan Bekasi** (termasuk kawasan industri Cikarang, Jababeka, MM2100) yang terbuka untuk lulusan **Jurusan Biologi (Fresh Graduate / Entry Level)**.

---

## 📋 Daftar Isi
1. [Fitur Utama](#-fitur-utama)
2. [Langkah & Cara Penggunaan Repositori](#-langkah--cara-penggunaan-repositori)
3. [Cara Memperbarui Data (Scraping Ulang)](#-cara-memperbarui-data-scraping-ulang)
4. [Penjelasan Hasil Output](#-penjelasan-hasil-output)
5. [Kustomisasi Kata Kunci & Lokasi](#-kustomisasi-kata-kunci--lokasi)
6. [Struktur Berkas Proyek](#-struktur-berkas-proyek)

---

## ✨ Fitur Utama

- 🌐 **Multi-Portal Scraping**: Mengambil data lowongan langsung dari **LinkedIn Guest API** (tanpa butuh login/akun) dan **Kalibrr Indonesia** (ekstraksi data terstruktur Next.js).
- 🧬 **Smart Biology Filter**: Otomatis menyaring posisi yang relevan dengan ranah ilmu biologi (Mikrobiologi, Analis Laboratorium, QC Pangan & Farmasi, R&D, Bioteknologi, Ekologi) dan membuang posisi yang salah sasaran (seperti QA Software atau Akuntansi).
- 📍 **Location Matcher**: Memfilter posisi khusus kawasan **Jakarta** dan **Bekasi / Cikarang**.
- 🎓 **Fresh Graduate Friendly**: Mendeteksi posisi yang ramah lulusan baru (pengalaman 0–1 tahun, entry-level, atau bertanda khusus *isOpenToFreshGrads*).
- 📊 **Multi-Format Export**: Menghasilkan file Excel (.xlsx) dengan link lamaran aktif, data CSV & JSON, serta **Web Dashboard Interaktif** lokal.
- 🛡️ **File-Lock Safe**: Jika Anda lupa menutup file Excel/CSV saat scraping dijalankan, program tidak akan error, melainkan otomatis menyimpan salinan terbaru bertanda waktu.

---

## 🚀 Langkah & Cara Penggunaan Repositori

Untuk mulai menggunakan repositori ini, ikuti salah satu cara berikut:

### Opsi A: Menggunakan Shortcut Runner (Paling Mudah & Cepat)
Anda **tidak perlu** repot mengaktifkan virtual environment secara manual:

- **Lewat PowerShell:**
  Buka terminal di folder project, lalu ketik:
  ```powershell
  .\run.ps1
  ```
- **Lewat File Explorer (Tanpa Buka Terminal):**
  Cukup buka folder `d:\web-scrap-biology` di Windows Explorer, lalu **klik ganda (double-click)** pada file [`run.bat`](file:///d:/web-scrap-biology/run.bat).

> Program akan otomatis mengumpulkan lowongan dan langsung membukakan **Web Dashboard interaktif** di browser default Anda (Chrome/Edge).

---

### Opsi B: Menggunakan Perintah Terminal Manual
Jika Anda ingin mengatur opsi tambahan via terminal PowerShell / Command Prompt:

```powershell
# 1. Jalankan langsung dengan Python Virtual Environment:
.\.venv\Scripts\python main.py --open-dashboard

# 2. Atau jika mengaktifkan virtual environment terlebih dahulu:
.\.venv\Scripts\Activate.ps1
python main.py --open-dashboard
```

---

## 🔄 Cara Memperbarui Data (Scraping Ulang)

Lowongan kerja di portal karir terus bertambah dan berganti setiap minggu. Anda bisa memperbarui data kapan saja untuk mendapatkan posisi kerja paling *fresh*.

### 1. Kapan Sebaiknya Memperbarui Data?
- **Secara berkala:** Disarankan menjalankan scraper **1–2 kali per minggu** agar tidak ketinggalan batas waktu (*deadline*) lamaran yang baru dibuka perusahaan.
- **Setiap kali mencari lowongan baru:** Cukup jalankan scraper sebelum Anda mulai menyortir dan mengirim lamaran kerja.

### 2. Langkah-Langkah Memperbarui Data:

> [!TIP]
> **Tips Penting Sebelum Update:**  
> Tutup terlebih dahulu aplikasi Microsoft Excel jika Anda sedang membuka file `lowongan_biologi_jabek.xlsx` atau `.csv`. Hal ini agar program dapat langsung menimpa file utama dengan data paling baru. (Jika lupa ditutup, program tetap aman dan akan menyimpannya ke file cadangan baru bertanda waktu).

1. Buka folder `d:\web-scrap-biology`.
2. Jalankan perintah pembaruan data:
   ```powershell
   .\run.ps1
   ```
### 3. Mode Realtime Cron Job (Auto-Refresh Tiap 5 Menit) ⏱️

Jika Anda ingin scraper berjalan secara otomatis terus-menerus di latar belakang dan memperbarui lowongan **setiap 5 menit secara realtime**:

- **Lewat PowerShell:**
  ```powershell
  .\start_auto_scraper.ps1
  ```
- **Lewat File Explorer:**
  Klik ganda (double-click) file [`start_auto_scraper.bat`](file:///d:/web-scrap-biology/start_auto_scraper.bat).
- **Atau lewat terminal manual:**
  ```powershell
  .\.venv\Scripts\python scheduler.py --interval 5
  ```

> 💡 **Fitur Live-Sync di Web Dashboard:**  
> Saat cron job ini berjalan, Anda cukup membiarkan tab [`dashboard.html`](file:///d:/web-scrap-biology/output/dashboard.html) tetap terbuka di browser. Halaman dashboard memiliki fitur **Live Polling** yang akan otomatis menyegarkan kartu lowongan dan statistik setiap kali cron job 5 menit selesai tanpa perlu refresh manual (`F5`)!

---

## 📊 Penjelasan Hasil Output

Semua hasil scraping disimpan di folder [`d:\web-scrap-biology\output\`](file:///d:/web-scrap-biology/output/):

| File | Format | Cara Membuka & Kegunaan |
| :--- | :--- | :--- |
| **`dashboard.html`** | 🌐 **Web Dashboard** | **Klik ganda** untuk membukanya di browser. Terdapat **fitur pencarian instan**, filter tombol **Jakarta** vs **Bekasi**, kartu lowongan lengkap dengan tag keahlian (`#mikrobiologi`, `#analis lab`), estimasi gaji, dan tombol **"Lamar Sekarang"** yang langsung mengarah ke website resmi perusahaan. |
| **`lowongan_biologi_jabek.xlsx`** | 📊 **Excel Spreadsheet** | Buka di Microsoft Excel. Sudah dirapikan dengan warna tema sains, lebar kolom otomatis, dan kolom link lamaran yang bisa langsung diklik. |
| **`lowongan_biologi_jabek.csv`** | 📄 **CSV** | Format tabel data standar untuk diolah di Google Sheets, SPSS, atau Python pandas. |
| **`lowongan_biologi_jabek.json`** | 🗄️ **JSON** | Data lengkap terstruktur berisi ID, judul, nama perusahaan, deskripsi lengkap pekerjaan, kualifikasi, dan gaji. |

---

## ⚙️ Kustomisasi Kata Kunci & Lokasi

Jika Anda ingin memperluas atau mempersempit pencarian (misalnya ingin menambahkan spesialisasi kultur jaringan atau memperluas area ke Karawang/Tangerang), Anda cukup mengedit file [`config.py`](file:///d:/web-scrap-biology/config.py):

1. **Menambah Posisi Biologi**:
   Buka `config.py` dan tambahkan kata kunci baru pada `BIOLOGY_KEYWORDS`:
   ```python
   BIOLOGY_KEYWORDS = [
       "biologi",
       "mikrobiologi",
       "analis laboratorium",
       "kultur jaringan",
       "qc pangan",
       "qc farmasi",
       "ahli lingkungan",  # <-- Contoh kata kunci baru
   ]
   ```

2. **Menambah / Mengubah Lokasi**:
   Pada `LOCATIONS_CONFIG` di `config.py`, Anda dapat menambahkan alias kawasan industri baru (seperti Cilegon, Serang, Karawang KIIC/Suryacipta).

Setelah mengedit `config.py`, cukup jalankan kembali `.\run.ps1` untuk mengambil lowongan dengan kriteria baru Anda.

---

## 📂 Struktur Berkas Proyek

```
d:\web-scrap-biology\
├── .venv/                      # Virtual Environment Python
├── config.py                   # Konfigurasi kata kunci biologi, lokasi, & headers
├── requirements.txt            # Daftar dependensi library
├── run.bat                     # Shortcut klik ganda untuk Windows Explorer
├── run.ps1                     # Shortcut eksekusi satu baris untuk PowerShell
├── main.py                     # Program utama (CLI runner)
├── README.md                   # Panduan lengkap proyek
├── scrapers/                   # Engine pengambil data
│   ├── base_scraper.py         # Skema data standar JobItem
│   ├── linkedin_scraper.py     # Scraper LinkedIn Guest API
│   └── kalibrr_scraper.py      # Scraper Kalibrr Indonesia
├── filters/                    # Filter cerdas
│   ├── biology_matcher.py      # Filter keilmuan biologi & lab
│   ├── location_matcher.py     # Filter lokasi Jakarta & Bekasi
│   └── freshgrad_matcher.py    # Filter level lulusan baru
├── exporters/                  # Modul pembuatan file output
│   ├── excel_exporter.py       # Generator spreadsheet Excel (.xlsx)
│   ├── csv_json_exporter.py    # Generator CSV & JSON
│   └── dashboard_exporter.py   # Generator Web Dashboard interaktif
└── output/                     # Direktori hasil scraping
    ├── dashboard.html          # Web Dashboard interaktif
    ├── lowongan_biologi_jabek.xlsx
    ├── lowongan_biologi_jabek.csv
    └── lowongan_biologi_jabek.json
```
