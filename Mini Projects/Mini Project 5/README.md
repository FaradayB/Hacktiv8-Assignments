# Mini Project 5 – IT Helpdesk RAG System

**Penulis:** Faraday Barr Fatahillah

---

## Deskripsi Proyek

Proyek ini membangun sistem **Retrieval-Augmented Generation (RAG)** untuk IT Helpdesk yang berjalan sepenuhnya secara lokal tanpa memerlukan API berbayar. Sistem ini mampu menerima pertanyaan atau laporan masalah IT, mengklasifikasikan kategorinya secara otomatis, mencari prosedur SOP yang relevan, lalu menghasilkan jawaban menggunakan LLM lokal melalui Ollama.

---

## Arsitektur Sistem

```
Query Pengguna
     │
     ▼
[1] Klasifikasi Kategori
    └─ TF-IDF + Logistic Regression
     │
     ▼
[2] Pencarian Konteks (Retrieval)
    └─ ChromaDB + SentenceTransformer (all-MiniLM-L6-v2)
     │
     ▼
[3] Generasi Jawaban
    └─ Ollama (llama3)
     │
     ▼
[4] Evaluasi Kualitas Jawaban
    └─ LLM-as-Judge (Groundedness · Coherence · Relevance)
```

| Komponen                       | Teknologi                                   |
| ------------------------------ | ------------------------------------------- |
| Klasifikasi tiket              | TF-IDF + Logistic Regression (scikit-learn) |
| Penyimpanan & pencarian vektor | ChromaDB (persisten)                        |
| Embedding teks                 | `all-MiniLM-L6-v2` (SentenceTransformers)   |
| Generasi jawaban               | Ollama (`llama3`)                           |
| Evaluasi kualitas              | LLM-as-Judge dengan 3 metrik                |

---

## Struktur File

```
mini_project_5/
├── mini_project_5_FaradayBarrFatahillah.ipynb   # Notebook utama
├── SOP_IT_Helpdesk_Mitsubishi.md                 # Dokumen SOP (diperlukan)
├── tickets_IT_helpdesk_150each.csv               # Dataset pelatihan klasifikasi
├── tickets_IT_helpdesk_testset_30each.csv        # Dataset pengujian
├── classifier.pkl                                # Model terlatih (dihasilkan)
├── results.jsonl                                 # Output RAG batch (dihasilkan)
├── results_evaluated.jsonl                       # Output evaluasi (dihasilkan)
├── chroma_db/                                    # Database vektor ChromaDB (dihasilkan)
├── requirements.txt                              # Dependensi Python
└── README.md                                     # Dokumentasi ini
```

---

## Prasyarat

### 1. Python

Python 3.10 atau lebih baru.

### 2. Ollama

Ollama harus terinstal dan berjalan di mesin lokal dengan model `llama3` yang sudah diunduh:

```bash
# Instal Ollama (lihat https://ollama.com untuk instruksi lengkap)
# Unduh model llama3
ollama pull llama3

# Pastikan server Ollama berjalan
ollama serve
```

### 3. Dependensi Python

```bash
pip install -r requirements.txt
```

---

## Cara Menjalankan

1. **Clone atau unduh** repositori ini.
2. **Siapkan file data** yang diperlukan di direktori yang sama dengan notebook:
   - `SOP_IT_Helpdesk_Mitsubishi.md`
   - `tickets_IT_helpdesk_150each.csv`
   - `tickets_IT_helpdesk_testset_30each.csv`
3. **Pastikan Ollama berjalan** dan model `llama3` telah diunduh.
4. **Jalankan notebook** secara berurutan dari Sel 0 hingga Sel 11:
   ```bash
   jupyter notebook mini_project_5_FaradayBarrFatahillah.ipynb
   ```

---

## Penjelasan Alur Notebook

| Sel | Judul                               | Keterangan                                                       |
| --- | ----------------------------------- | ---------------------------------------------------------------- |
| 0   | Konfigurasi Global                  | Mendefinisikan konstanta model, path, dan kategori valid         |
| 1   | Pelatihan Klasifikasi               | Melatih TF-IDF + Logistic Regression, menyimpan `classifier.pkl` |
| 2   | Parsing SOP & Pengindeksan ChromaDB | Mengurai dokumen SOP menjadi chunks dan mengindeksnya            |
| 3   | Muat Ulang Classifier               | Memuat model dari `classifier.pkl`                               |
| 4   | `classify_query()`                  | Fungsi klasifikasi kategori tiket                                |
| 5   | `retrieve()`                        | Fungsi pencarian SOP relevan dari ChromaDB                       |
| 6   | `response_generate()`               | Fungsi generasi jawaban via Ollama + RAG                         |
| 7   | Inferensi Batch                     | Menjalankan pipeline RAG pada seluruh data uji                   |
| 8   | Fungsi Evaluasi                     | Mendefinisikan LLM-as-Judge untuk 3 metrik                       |
| 9   | Evaluasi Batch                      | Mengevaluasi semua hasil RAG                                     |
| 10  | Statistik Ringkasan                 | Menampilkan rata-rata, min, max, std setiap metrik               |
| 11  | Record Bermasalah                   | Menampilkan tiket dengan skor evaluasi rendah                    |

---

## Metrik Evaluasi

Sistem menggunakan **LLM-as-Judge** dengan tiga metrik, masing-masing dengan skala **1–5**:

| Metrik           | Definisi                                                                    |
| ---------------- | --------------------------------------------------------------------------- |
| **Groundedness** | Apakah setiap klaim dalam jawaban didukung oleh konteks SOP yang diberikan? |
| **Coherence**    | Apakah jawaban terstruktur dengan logis, lancar, dan mudah diikuti?         |
| **Relevance**    | Apakah jawaban secara langsung menjawab pertanyaan pengguna?                |

Tiket dengan skor di bawah **3** pada salah satu metrik akan ditandai untuk analisis lebih lanjut.

---

## Kategori Tiket yang Didukung

| Kategori     | Cakupan                                             |
| ------------ | --------------------------------------------------- |
| **Access**   | Masalah autentikasi, MFA, reset password, hak akses |
| **Network**  | Konektivitas jaringan, VPN, WiFi, pengaturan proxy  |
| **Hardware** | Kerusakan perangkat fisik, printer, monitor, laptop |
| **Software** | Instalasi/error aplikasi, ERP/SAP, Microsoft Office |

---

## Catatan Penting

- Sel 1 (pelatihan) hanya perlu dijalankan sekali. Setelah `classifier.pkl` tersimpan, gunakan Sel 3 untuk memuat ulang.
- ChromaDB menyimpan data secara persisten di `./chroma_db`. Sel 2 akan menghapus dan membuat ulang koleksi setiap kali dijalankan.
- Kualitas jawaban sangat bergantung pada kelengkapan dokumen `SOP_IT_Helpdesk_Mitsubishi.md`.
- Waktu eksekusi Sel 7 dan Sel 9 bergantung pada kecepatan Ollama di mesin lokal Anda.
