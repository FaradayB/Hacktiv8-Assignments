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
&nbsp;

#### [3] Prompt Design

**A - System Prompt**
Berikut merupakan prompt design yang digunakan:

```python
"""
#Persona
You are a virtual health assistant for BPJS Kesehatan Class 1 members in Indonesia.

#Scope
Only answer questions related to:
- Common health symptoms and complaints
- Basic first-aid steps
- BPJS Class 1 service procedures and information
- Recommendations for primary healthcare facilities (puskesmas, clinics)

#Format
Structure every answer as follows:
1. Brief explanation of the symptom (1-2 sentences)
2. Steps the user can take (bullet points)
3. Action recommendation (visit a facility or manage at home)

#Language
- Always respond in Bahasa Indonesia.
- Use a friendly, empathetic tone that is easy for the general public to understand.
- Avoid overly technical medical terminology.

#Refusal
- NEVER directly diagnose any disease or medical condition
- NEVER recommend prescription drug dosages
- NEVER answer questions outside the topics of health and BPJS
- Always recommend consulting a doctor for serious or unclear conditions
"""
```

&nbsp;

**B - Context / RAG Injection**

```HTML
<context>
[FAQ Kesehatan Umum Kemenkes RI, WHO, Research Paper — ~300 token per chunk]
[Panduan Faskes BPJS Kelas 1 — ~200 token per chunk]
</context>
```

&nbsp;

**C - Sample User Messages**

```
MSG1: "Anak saya demam 38.5 derajat sejak kemarin, apa yang harus saya lakukan?"
MSG2: "Apakah saya dapat menggunakan BPJS untuk cek kuping yang berinfeksi di THT?"
MSG3: "Saya merasa pusing dan terlihat pucat serta gemetaran, apa ada obat yang bisa membantu?"
```

&nbsp;

**D - Expected Ouput Definition**
| Komponen | Jawaban |
|----------|-------------------------|
|Format | bullet list |
|Length | medium ~200 |
|Tone | friendly and empathetic |
|Language | Bahasa Indonesia |

```
Sample OK:
Ya, kamu dapat menggunakan BPJS kelas 1 kamu untuk ke dokter THT, namun dengan alur berikut:
1. Kunjungi faskes tingkat pertama terdaftar di kartu BPJS kamu,
2. Minta surat rujukan ke dokter spesialis THT,
3. Datang ke poliklinik THT rumah sakit dengan surat rujukan tersebut.
```

&nbsp;
&nbsp;

#### [4] Token Estimation

| Measure           | Token |
| ----------------- | ----- |
| System Prompt     | 200   |
| Avg. User Message | 22    |
| Avg. Context/RAG  | 500   |
| Expected Output   | 250   |

```
Total Tokens = Sys + User + Context + Output = 200 + 22 + 500 + 250 =  972
```

&nbsp;
&nbsp;

#### [5] Cost Estimation

Terdapat 2 case, yaitu high volume dan low volume. Berikut merupakan perhitungan cost dari dua case tersebut.

Pricing terdapat pada dokumentasi [Official Claude Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

**Low Volume**
| Measure | Token and Price |
| ----------------- | ----- |
| System Prompt | 200 Tokens |
| Avg. User Message | 22 Tokens |
| Avg. Context/RAG | 500 Tokens |
| Expected Output | 250 Tokens |
| Total input | 722 Tokens |
| Total Output | 250 Tokens |
| Expected Calls | 300 |
| Call per Month | 9000 |
| Input Price | $3 |
| Output Price | $15 |

```
Monthly Cost  =  ( Input tokens/call × calls/month ÷ 1,000,000 × input price )  +  ( Output tokens/call × calls/month ÷ 1,000,000 × output price )

Monthly Cost  =  ( 722 × 9000 ÷ 1,000,000 × 3 )  +  ( 250 × 9000 ÷ 1,000,000 × 15 ) = $19.5 + $33.75 = $53.25
```

**High Volume**
| Measure | Token and Price |
| ----------------- | ----- |
| System Prompt | 200 Tokens |
| Avg. User Message | 22 Tokens |
| Avg. Context/RAG | 500 Tokens |
| Expected Output | 250 Tokens |
| Total input | 722 Tokens |
| Total Output | 250 Tokens |
| Expected Calls | 3000 |
| Call per Month | 90000 |
| Input Price | $3 |
| Output Price | $15 |

```
Monthly Cost  =  ( Input tokens/call × calls/month ÷ 1,000,000 × input price )  +  ( Output tokens/call × calls/month ÷ 1,000,000 × output price )

Monthly Cost  =  ( 722 × 90000 ÷ 1,000,000 × 3 )  +  ( 250 × 90000 ÷ 1,000,000 × 15 ) = $195 + $3375 = $3570
```

PS:
Kurang tahu perhitungan benar atau tidak, rumus sedikit ambigu.
