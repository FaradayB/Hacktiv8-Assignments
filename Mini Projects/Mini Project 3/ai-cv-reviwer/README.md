# 🤖 AI Recruiter Pro - CV Evaluator

Aplikasi berbasis web untuk mengevaluasi CV/Resume kandidat secara otomatis menggunakan AI (Google Gemini 1.5 Flash). Aplikasi ini dirancang khusus untuk membantu HRD atau Tech Recruiter dalam menyaring kandidat **AI Engineer** berdasarkan keahlian teknis, pengalaman, portofolio, dan pendidikan.

Aplikasi ini menggunakan arsitektur terpisah:

- **Backend**: FastAPI (Memproses PDF dan memanggil API AI)
- **Frontend**: Streamlit (Antarmuka pengguna/UI yang interaktif)

---

## 📂 Struktur Direktori Proyek

Pastikan file kamu tersusun dalam satu folder dengan format direktori seperti berikut:

```text
AI-Recruiter-Pro/
│
├── backend.py         # File server FastAPI, ekstraksi PDF, & Prompt AI (Gemini)
├── frontend.py        # File antarmuka web menggunakan Streamlit
├── requirements.txt   # Daftar library Python yang dibutuhkan
└── README.md          # Dokumentasi panduan penggunaan aplikasi
```

---

## 🛠️ Persiapan & Instalasi Library

Sebelum menjalankan aplikasi, pastikan komputer kamu sudah terinstal Python (versi 3.8 ke atas). Ikuti langkah-langkah berikut untuk menginstal semua kebutuhan proyek:

1. **Dapatkan API Key Google Gemini**
   - Buka Google AI Studio dan login dengan akun Google kamu.
   - Klik "Get API Key" dan salin kunci rahasia tersebut.
   - Buka file backend.py, cari variabel API_KEY, dan masukkan kunci kamu:

   ```Python
   API_KEY = "MASUKKAN_API_KEY_GEMINI_KAMU_DISINI"
   ```

2. **Instal Library Python**
   Buka Terminal / Command Prompt, arahkan ke folder proyek (AI-Recruiter-Pro), lalu jalankan perintah ini untuk menginstal semua library yang ada di requirements.txt:

   ```Bash
   pip install -r requirements.txt
   ```

---

## 🚀 Langkah-Langkah Menjalankan Aplikasi

Karena aplikasi ini menggunakan arsitektur Client-Server, kamu harus menjalankan Frontend dan Backend secara bersamaan menggunakan 2 Terminal yang berbeda.
**Langkah 1: Jalankan Backend (Server FastAPI)**

1. Buka Terminal 1.
2. Arahkan ke folder proyek ini.
3. Jalankan perintah berikut:
   ```Bash
   uvicorn backend:app --reload
   ```
4. Biarkan terminal ini tetap terbuka. Server backend kini berjalan di http://127.0.0.1:8000.

**Langkah 2: Jalankan Frontend (Aplikasi Streamlit)**

1. Buka Terminal 2 (jendela terminal baru).
2. Arahkan ke folder proyek yang sama.
3. Jalankan perintah berikut:
   ```Bash
   streamlit run frontend.py
   ```
4. Browser akan otomatis terbuka dan menampilkan antarmuka aplikasi di http://localhost:8501.

---

## 💡 Cara Menggunakan Aplikasi

1. Buka aplikasi di browser (biasanya terbuka otomatis setelah menjalankan frontend.py).
2. Pada panel sebelah kiri layar, temukan area Upload Resume.
3. Klik Browse files atau drag-and-drop file CV kandidat (Pastikan file berformat .pdf).
4. Setelah muncul notifikasi file berhasil dipilih, klik tombol biru "Evaluate Candidate 🚀".
5. Tunggu beberapa saat selagi AI menganalisis dokumen.
6. Laporan evaluasi lengkap (Ringkasan, Kelebihan, Kekurangan, Kalkulasi Skor, dan Rekomendasi) akan muncul dengan rapi di panel utama sebelah kanan.

---

## ⚠️ Catatan Penting

- Kualitas PDF: Pastikan file PDF yang diunggah berisi teks digital yang bisa di-blok/disalin (bukan hasil scan berupa gambar), karena sistem menggunakan PyPDF2 untuk mengekstrak teks.
- Koneksi Internet: Aplikasi membutuhkan koneksi internet yang stabil untuk mengirim data dan menerima hasil evaluasi dari server Google Gemini AI.
