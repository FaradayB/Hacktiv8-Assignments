A short `README.md` (5–10 sentences) describing:

- What domain/documents you chose and why
- Which optimization techniques you implemented
- Your key findings from the comparison report
- One thing you'd do differently next time

---

Pada tugas ini, saya memilih domain/document dari salah satu game yang saya tamatkan, yaitu Trails of Cold Steel 1. Game ini memiliki cerita yang cukup kompleks dengan perpaduan antara peperangan, magic, kombat turn-based, dan cerita mengenai konflik politik. Namun, untuk mempermudah model mempelajarinya, diberikan dokumen yang cukup general mengenai game ini as a whole untuk membuat dokumen yang diberikan tidak terlalu panjang. Dokumen ini based dari pengetahuan saya sendiri, Wikipedia, dan laman Fandom yang tersedia online.

Model menggunakan optimasi seperti RRF (untuk cek keyword dan semantic), Chain-of-verification (untuk verifikasi ulang agar tidak halusinasi), ExactMatchCache (agar data secure dan bisa di cek lagi jika query yang sama diberikan lagi), dan Map Reduce (untuk dapat memproses secara paralel).

Beberapa insight yang saya dapatkan adalah model bekerja dengan baik untuk query yang sangat relevan dengan dokumen yang disediakan, seperti pada contoh query "Who is Rean?" dan dapat memberikan jawaban yang sesuai dengan dokumen. Namun, model ini tidak dapat stabil saat query yang diberikan merupakan informasi tambahan, seperti permasalahan politik erebonia. Hal yang dilakukan untuk ini sebenarnya lebih baik menggunakan basic RAG dibandingkan menggunakan yang optimized, karena yang optimized memiliki metric faith, relevance, dan precision yang lebih rendah.

Hal yang saya akan lakukan selanjutnya adalah menggunakan metode-metode lain seperti Cross-Encoder re-ranker, Self-RAG, Citation Prompting,Semantic Cache, dan Refinement untuk mengetahui lebih lanjut teknik mana saja yang dapat memiliki performa yang lebih baik dan cost yang lebih efisien untuk dokumen ini. Selain itu, saya juga akan menambahkan beberapa informasi yang relevan mengenai topik.
