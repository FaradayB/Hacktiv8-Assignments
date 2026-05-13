# Assignment Sesi 23

Nama: Faraday Barr Fatahillah

---

### Product: AI Symptom Checker & Health FAQ Bot

#### [1] Project Scope and Goals

**What does your AI do?**
Sebuah chatbot informasi kesehatan untuk memahami gejala umum penyakit sehari-hari dan memberikan panduan pertolongan pertama secara sederhana. Selain itu, memberikan rekomendasi atau keputusan untuk pergi mendapatakan pertolongan dari profesional.
&nbsp;

**Who are the users?**
Masyarakat umum
&nbsp;

**What does 'Success' look like?**

- Jawaban aman secara medis dan selalu menyarankan "konsultasi ke dokter" bila diperlukan,
- Respons diberikan dalam waktu yang kurang dari 3 detik,
- Dapat mengambil makna dari user walaupun input beracak-acakan,
- Memberikan ketenangan ke user dalam keadaan panik.
  &nbsp;

**What are your hard constraints?**

- Wajib dalam Bahasa Indonesia,
- Tidak menyalah gunakan data medis yang di input user,
- Gratis bagi yang memiliki BPJS kesehatan,
- Dapat mendeteksi gambar penyakit yang dialami dan generate beberapa possibility penyakit yang dialami tanpa membuat user panik, tetapi merekomendasikan user untuk mendatangi profesional,
- Tidak merekomendasikan lifestyle tanpa research dari website-website ternama.
  &nbsp;

**What data will you feed the model?**

- Panduan kesehatan umum dari WHO, Kemenkes RI, dan Internationally approved hospitals,
- Research Paper yang terbaru dengan informasi yang lengkap,
- Hasil riset mandiri yang didampingi dan di approve oleh dokter-dokter,
- Panduan menjawab dengan bahasa yang halus, formal, dan informatif.
  &nbsp;

#### [2] Model Selection (Scale 1-3)

| Model             | Quality | Speed | Cost | Constraint | Total |
| ----------------- | ------- | ----- | ---- | ---------- | ----- |
| Claude Haiku 4.5  | 2       | 3     | 3    | 2          | 10    |
| Claude Sonnet 4.6 | 3       | 2     | 3    | 3          | 11    |
| Gemini 2.5 Flash  | 2       | 3     | 1    | 1          | 7     |
| GPT-5 Mini        | 1       | 3     | 1    | 2          | 7     |
| Gemini 2.0 Flash  | 1       | 2     | 2    | 1          |

Sesuai dengan hasil konsiderasi di atas, Claude Sonnet 4.6 sangat cocok untuk use case ini karena merupakan model dengan kualitas terbaik, cepat, dan dapat menyesuaikan dengan constraint yang ditentukan.
&nbsp;

#### [3] Prompt Design

**A - System Prompt**
Berikut merupakan prompt design yang digunakan:

```python
"""
Kamu adalah asisten kesehatan virtual untuk peserta BPJS Kesehatan Kelas 1 Indonesia.

Bantu pengguna memahami gejala umum, panduan pertolongan pertama, dan kapan harus
ke dokter atau fasilitas kesehatan terdekat.

Jawab hanya pertanyaan seputar kesehatan
umum dan informasi BPJS. Jangan pernah mendiagnosis penyakit secara langsung.

Selalu sarankan konsultasi dokter untuk kondisi serius. Respond dalam Bahasa Indonesia
yang ramah dan mudah dipahami. Kembalikan jawaban dalam format poin-poin singkat
diikuti rekomendasi tindakan.
"""
```

&nbsp;

**B - Context / RAG Injection**
