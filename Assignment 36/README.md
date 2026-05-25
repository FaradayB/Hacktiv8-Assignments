# Medical First-Aid RAG Assistant

Proyek ini adalah aplikasi **Retrieval-Augmented Generation (RAG)** berbasis pertolongan pertama medis yang dibangun menggunakan model bahasa lokal melalui Ollama. Sistem ini mengambil dokumen relevan dari knowledge base, lalu menggunakannya sebagai konteks untuk menghasilkan jawaban yang akurat dan aman.

---

## Prasyarat

Sebelum menjalankan notebook, pastikan semua dependensi berikut sudah terinstal di sistem kamu.

### 1. Python

Gunakan Python versi **3.10 atau lebih baru**. Disarankan menggunakan virtual environment:

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 2. Ollama (Model Lokal)

Proyek ini menggunakan Ollama sebagai runtime model lokal. Unduh dan instal dari:

👉 https://ollama.com/download

Setelah terinstal, jalankan Ollama di terminal terpisah:

```bash
ollama serve
```

Lalu tarik kedua model yang dibutuhkan:

```bash
ollama pull llama3.2
ollama pull gemma3:4b
```

> **Catatan:** `llama3.2` adalah model utama (PRIMARY_MODEL) dan `gemma3:4b` adalah model pembanding (SECONDARY_MODEL). Pastikan keduanya sudah berhasil di-pull sebelum menjalankan notebook.

### 3. Dependensi Python

Instal semua library yang diperlukan dengan perintah berikut:

```bash
pip install ollama chromadb sentence-transformers python-dotenv numpy pandas jupyter
```

Atau jika tersedia file `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Konfigurasi Environment

Buat file `.env` di direktori yang sama dengan notebook, lalu isi dengan konfigurasi berikut:

```env
PRIMARY_MODEL=llama3.2
SECONDARY_MODEL=gemma3:4b
```

Kamu bisa mengganti nilai ini dengan model Ollama lain yang sudah kamu pull, jika diinginkan.

---

## Cara Menjalankan Notebook

Pastikan Ollama sedang berjalan (`ollama serve`), lalu jalankan Jupyter:

```bash
jupyter notebook
```

Buka file `assignment_sesi_36_FaradayBarrFatahillah.ipynb` dan jalankan cell secara berurutan dari atas ke bawah (**Run All** atau **Shift + Enter** per cell).

### Urutan Eksekusi Cell

| Cell | Keterangan |
|------|-----------|
| **B.0** | Setup awal — impor library, konfigurasi model, uji koneksi Ollama |
| **B.1** | Memuat 15 dokumen pertolongan pertama ke ChromaDB, uji fungsi `retrieve()` |
| **B.2** | Membangun fungsi `ask()` — RAG pipeline lengkap (retrieve → prompt → generate) |
| **B.3** | Membuat dataset evaluasi 20 baris dan menyimpannya ke `eval_dataset.jsonl` |
| **B.4** | Menjalankan 7 evaluator (5 kualitas + 2 keamanan), hasil disimpan ke `eval_results.json` |
| **B.5** | Menjalankan custom evaluator `language_match`, hasil disimpan ke `eval_results_with_custom.json` |
| **B.6** | Red teaming — menguji 10 prompt adversarial, hasil disimpan ke `red_team_report.json` |
| **B.7** | Membandingkan dua model (`llama3.2` vs `gemma3:4b`), hasil disimpan ke `model_comparison.csv` |
| **B.8** | Refleksi tertulis — tidak ada kode yang dijalankan |

---

## File Output yang Dihasilkan

Setelah notebook selesai dijalankan, file-file berikut akan terbuat secara otomatis:

| File | Deskripsi |
|------|-----------|
| `eval_dataset.jsonl` | Dataset evaluasi 20 baris (query, response, context, ground_truth) |
| `eval_results.json` | Hasil evaluasi 7 evaluator standar |
| `eval_results_with_custom.json` | Hasil evaluasi termasuk custom evaluator `language_match` |
| `red_team_report.json` | Laporan red teaming — daftar probe dan hasil penilaian |
| `eval_llama3_2.jsonl` | Hasil inferensi model `llama3.2` untuk perbandingan |
| `eval_gemma3_4b.jsonl` | Hasil inferensi model `gemma3:4b` untuk perbandingan |
| `eval_results_llama3_2.json` | Metrik evaluasi model `llama3.2` |
| `eval_results_gemma3_4b.json` | Metrik evaluasi model `gemma3:4b` |
| `model_comparison.csv` | Tabel perbandingan kedua model secara berdampingan |

---

## Troubleshooting

**Ollama tidak bisa dihubungi (`Could not reach Ollama`):**
Pastikan `ollama serve` sudah berjalan di terminal yang terpisah. Periksa apakah Ollama berjalan di port default `11434`.

**Model belum tersedia (`model not found`):**
Jalankan `ollama pull llama3.2` dan `ollama pull gemma3:4b` sebelum menjalankan notebook.

**Error saat instal `chromadb` atau `sentence-transformers`:**
Pastikan versi Python kamu ≥ 3.10. Pada beberapa sistem, mungkin perlu menginstal `build-essential` (Linux) atau `Microsoft C++ Build Tools` (Windows) terlebih dahulu.

**Cell B.4 atau B.5 berjalan sangat lama:**
Ini normal — setiap baris di dataset evaluasi memerlukan beberapa panggilan ke model lokal. Waktu total tergantung spesifikasi hardware kamu. GPU sangat disarankan untuk mempercepat proses.

---

## Struktur Direktori

```
.
├── assignment_sesi_36_FaradayBarrFatahillah.ipynb  # Notebook utama
├── .env                                             # Konfigurasi model (buat manual)
├── README.md                                        # Dokumentasi ini
├── eval_dataset.jsonl                               # (dihasilkan saat runtime)
├── eval_results.json                                # (dihasilkan saat runtime)
├── eval_results_with_custom.json                    # (dihasilkan saat runtime)
├── red_team_report.json                             # (dihasilkan saat runtime)
└── model_comparison.csv                             # (dihasilkan saat runtime)
```

---

## Catatan Penting

Proyek ini berjalan **sepenuhnya secara lokal** tanpa memerlukan akses ke Azure AI Foundry atau Azure OpenAI. Semua proses inferensi dan evaluasi menggunakan model yang berjalan di mesin kamu sendiri melalui Ollama. Pastikan kamu memiliki minimal **8 GB RAM** dan disarankan menggunakan **GPU** agar proses berjalan dalam waktu yang wajar.
