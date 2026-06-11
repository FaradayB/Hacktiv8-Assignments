# Assignment Sesi 34

Nama: Faraday Barr Fatahillah

## Soal:

Skenario:
MMKSI ingin membuat aplikasi yang dapat membantu car owners untuk membuat janji servis online, unggah foto permasalahan mobil, mendapatkan update secara real-time, dan memberikan rating kepada dealer setelah servis.

Key Challenges:

- Koneksi secara nasional dengan latency kecil
- Dapat upload foto dari mobile (dengan network yang bervariasi)
- Ada notif real-time untuk status update
- Integrasi dengan sistem dealer yang sudah ada
- Mengikuti undang-undang data residency di Indonesia

Key Numbers:

- 500k User
- 50k active user per bulan
- 5k user saat peak
- Availability 99.95%
- page load kurang dari 2s
- Beroperasi 24/7

Requirements:
a. Fungsional

- Ada integrasi user dan manajemen profil (F1)
- Bisa booking dan reschedule servis (F2)
- Upload photo (F3)
- Notif real-time (F4)
- Scheduler management pada sisi dealer (F5)
- Post-service rating dan feedback (F6)
- Management analytics dashboard (F7)
- Integrasi dengan sistem dealer yang sudah ada (F8)

b. Non fungsional

- Availability >= 99.95% (N1)
- P95 page load kurang dari 2s (N2)
- Auto-scaling untuk peak 5k user (N3)
- Enkripsi pada Rest dan Transit (N4)
- Ada daily backup dengan retensi data selama 30 hari (N5)
- RTO kurang dari 4 jam dan RPO kurang dari 1 jam (N6)
- Mengikuti undang-undang data residency (N7)
- Monitoring dan alerting central (N8)

---

## Answer:

Aplikasi yang dikembangkan adalah mobile web app sehingga bisa menggunakan Azure Front Door Sebagai produk utama yang akan digunakan.

---

### Architecture Diagram

Setiap produk Azure yang digunakan pada projek ini menyesuaikan dengan requirements yang ditentukan baik fungsional (F1-F8) dan non-fungsional (N1-N8).

1. **Azure Front Door (Premium)** \
   Service ini dipilih karena dapat menjadi single global entry point yang sudah memiliki Web Application Firewall (termasuk TOP 10 OWASP), CDN, DDoS and bot protection, dan global load balancing dalam satu service. Selain itu, service ini support private link ke backend origins agar zero-IP exposure. Perlu di catat bahwa pilihan service ini harus yang tier Premium karena tier ini yang mendapatkan private link tersebut dan WAF yang bisa di manage.

2. **Azure CDN**\
   Azure CDN digunakan sebagai CDN terpisah untuk gambar dan foto agar tidak mengganggu load dari Azure Front Door.

3. **Azure Container Apps (ACA)** \
   Service ini dipilih untuk memberikan auto-scaling yang terjadi based on event. Selain itu, terdapat scale-to-zero yang dapat memberikan cost yang lebih efisien. Kemudian, terdapat Dapr integration yang idel untuk melakukan booking, rating, analytics, dan koneksi API dengan aplikasi dealer. Service ini juga dapat handle 5K user saat peak hours tanpa pengaplikasian operasional Kubernetes. Azure Container Apps ini akan di konfigurasikan di Jakarta sebagai primary dan secondary di region yang lebih dekat seperti Singapur, Malaysia, atau Hong Kong.

4. **Azure Functions** \
   Azure Functions digunakan untuk async workloads saja, seperti resize foto (F3), notifikasi (F4), dan management analytics (F7). Selain itu, service ini bentuknya serverless jadi saat idle tidak akan terkena biaya.

5. **Azure SQL Database** \
   Dipilih karena digunakan untuk melakukan booking appointment servis (F7), dealer schedule management (F5), dan manajemen profil user (F1) yang membutuhkan ACID transaction, relational joins, dan konsisten. Selain itu, perlu memilih Business-Critical tier yang memberikan built-in in-memory OLTP dan 4-replica Always On dengan 99.99% SLA (N1).

6. **Azure Cache for Redis** \
   Digunakan agar caching jadwal dealer, session tokens, dan data yang sering digunakan kembali sehingga mengurangi pengambilan data dari datase dan support P95 < 2s page load (N2). Service ini juga shared ke semua Azure Container Apps replicas.

7. **Azure Blob Storage** \
   Menyimpan foto yang diberikan user dan memiliki Zone-redundant storage yang memastikan 12-nines durability di region utama. Selain itu akan mengubah foto yang sudah lebih lama dari 90 hari ke Cool tier dan meng-Archive selama 365 hari sehingga bisa mengontrol cost penyimpanan.

8. **Azure Service Bus** \
   Service ini memberikan jaminan untuk melakukan pengiriman minimal sekali, dead letter queues untuk pesan yang gagal terkirim, dan bisa berintegrasi dengan sistem manajemen eksternal (F8). Selain itu, dapat memisahkan alur permintaan pemesanaan dari proses konfirmasi dealer (F2). Pilih tier yang standard untuk dapat memenuhi beberapa requirements fungsional.

9. **Azure Notification Hubs** \
   Service ini memungkinkan untuk mengirim real-time push notification ke IOS dan Android yang dapat mengirim 10 juta push per bulan dan bisa bertambah 100 juta jika memang di butuhkan (F4). Selain itu, harus memilih fitur standard untuk menggunakan fitur tersebut, ditambah dengan kebutuhan device yang aktif, coverage SLA, dan Scheduled Push.

10. **Azure Communication Services** \
    Memberikan layanan pengiriman SMS dan email melalui satu API yang dikelola oleh Azure. Hal ini mempermudah untuk tidak perlu mengelola gateway SMTP atau provider SMS.

11. **Microsoft Entra External ID** \
    Servis yang dapat login menggunakan media sosial, seperti Google dan Facebook, OTP, MFA, dan login menggunakan akun khusus aplikasi. Servis ini mempermudah integrasi customer dalam pembuatan akun dan profil pada aplikasi.

12. **RBAC Roles** \
    Menerapkan hak akses minimal untuk ACA, Functions, Database yang memiliki identitas terkelola sehingga mudah untuk melakukan manajemen per servis tanpa perlu kredensial statis.

13. **Azure Key Fault** \
    Untuk menyimpan semua secrets, API keys, sertifikat TLS, dan jaringan sehingga tidak perlu hardcode environment variables.

14. **Azure Application Insights** \
    Tracing semua ACA microservices dan fungsi, memberikan P95 latency tracking (N2), exception logging, dependency maps, dan dashboard custome untuk analytics (F7).

15. **Log Analytics Workspace** \
    Mengsentralisasi seluruh log dari semua service yang digunakan yang mengaktivasi KQL queries untuk security audit, invesitgasi performa, dan backup verifikasi otomatis selama 30 hari (N5).

16. **Azure Monitor + Alerts** \
    Mengsentralisasi kebobolan SLA, CPU/Memory thresholds, deployment gagal, dan traffic pattern yang anomali (N8).

### Coverage Non-fungsiona

1. Availability (N1) \
   Memiliki SLA yang lebih dari 99.95% (N1). Berikut merupakan setiap konfigurasi bersama SLA nya.

   | Tier                                 | SLA (%) |
   | ------------------------------------ | ------- |
   | Azure Front Door Premium             | 99.99%  |
   | Azure Container Apps                 | 99.95%  |
   | Azure SQL Database Buisness-Critical | 99.99%  |
   | Azure Cache for Redis P2             | 99.9%   |
   | Azure Blob Storage                   | 99.9%   |

   Melihat tabel di atas, kriteria dapat terpenuhi dengan targe mendapatkan 99.95% availability

2. P95 pge load < 2 detik (N2) \
   Waktu Pemuatan Halaman P95 < 2 Detik (N2)
   Optimasi latensi berlapis:
   - Azure Front Door CDN: Aset statis (JS, CSS, gambar) disimpan dalam cache di PoP tepi yang terdekat dengan pengguna di Indonesia
   - Azure Cache for Redis: Jadwal dealer dan data sesi disajikan dalam waktu < 5 ms dari cache
   - Application Insights: Dasbor latensi P95 dikonfigurasi dengan peringatan pada ambang batas 1,5 detik untuk peringatan dini
   - Penskalaan horizontal ACA: Mencegah lonjakan latensi yang dipengaruhi CPU selama puncak 5 ribu pengguna bersamaan

3. Auto-scaling untuk handle 5k user secara bersamaan (N3) \
   Azure Container Apps dikonfigurasi dengan aturan penskalaan HTTP berbasis KEDA:
   - Jumlah replika minimum: 2 (selalu dalam keadaan siap, tanpa cold start untuk API inti)
   - Jumlah replika maksimum: 20 (per layanan mikro)
   - Pemicu penskalaan: Ambang batas koneksi HTTP bersamaan sebesar 250 per replika
   - Waktu penskalaan: < 30 detik melalui penskala HTTP KEDA bawaan ACA

   Azure Functions (pemrosesan foto, pemberitahuan) melakukan penskalaan secara independen melalui model konsumsi berbasis peristiwa dan tidak memerlukan konfigurasi.

4. Enkripsi saat Rest dan Transit (N4)
   - Saat Transit: semua endpoint memaksa HTTPS via SSL offload Azure Front Door
   - Saat Rest: database menggunakan Transparent Data Encryption dengan kunci dikelola di Key Vault, Blob Storage menggunakan SSE-256, dan enkripsi Redis di aktifkan saat Rest
   - Semua kredensial ada di Key Vault yang diakses melalui managed identity dan tidak perlu plaintext lewat environment manapun.

5. Daily Automated Backups, 30-Day Retention (N5)
   | Service | Retention |
   |---------|-----------|
   | Azure SQL Database | 30 hari (bisa dikonfigurasikan) |
   | Azure Blob Storage | 30 hari |
   | Azure Cache for Redis | 7 hari, hanya untuk caching saja |

6. Disaster Recovery (N6) \
   Contoh jika replica terdapat di Hong Kong menggunakan Active Geo-Replication
   | Sertvice | RTO | RPO |
   |----------|-----|-----|
   | Azure SQL Database | > 60 detik | ~0 detik |

7. Data Residency di Indonesia (N7)
   - Primary region: Southeast Asia (Jakarta)
   - Semua production data disimpan di Primary Region
   - Secondary Region hanya digunakan saat ada bencana
   - Transfer data smeua terenkripsi secara end-to-end

8. Monitoring dan Alerting Sentral (N8)
   - Application Insights memberikan semua telemetry ke satu Log Analytics Workspace
   - Azure Monitor memberitahu jika, pembobolan SLA, latency P95 lebih dari 2 detik, banyak autentikasi yang gagal, DTU database lebih dari 85%, dan kapasitas penyimpanan lebih dari 80%
   - Alert dikirimkan ke Email dan Microsoft Teams webhook
   - Bisa melakukan synthetic monitoring

### Cost Perbulan

Berikut merupakan link [ini](https://azure.com/e/aaf89fd4cb7c476dadc17beb76319a5c). Berikut merupakan pricing per bulan dan per tahun dari setiap servis.
| Service | Per Bulan ($) | Per Tahun ($) | Keterangan |
|---------|---------------|---------------|------------|
| Azure SQL Database | 5,141.27 | 61,695.19 | - |
| Azure Front Door | 1,049.28 | 12,591.36 | - |
| Content Delivery Network (CDN) | 342.27 | 4,107.18 | - |
| Azure Container Apps | 144.43 | 1,733.18 | = |
| Azure Functions | 33.50 | 402.00 | - |
| Azure Cache for Redis | 618.26 | 7,419.17 | - |
| Service Bus | 9.81 | 117.74 | - |
| Noticication Hubs | 200.00 | 2,400.00 | - |
| Azure Communication Services | 3,685.00 | 44,220.00 | - |
| Microsoft Entra External ID | 0 | 0 | Tidak ada tambahan biaya untuk 50k core active user |
| Key Vault | 9.45 | 113.40 | - |
| Azure Monitor | 508.32 | 6,099.82 | - |
| Azure Blob Storage | - | - | Tidak tersedia di pricing calculator |
| **Total** | 11,770.59 | 141,247.04 | |

Rupiah Sekarang = Rp. 17,698.60
Per month = Rp. 208,322,964.17
Per year = Rp. 2,499,874,862.14

NOTE: Harga di atas belum include Blob Storage jika ditambahkan Blob Storage dapat menjadi estimasinya $15,000 per bulan (paling murah). Communication Service masih dalam United States karena tidak ada pilihan nomor kode negara yang lain.

### Trade-offs & Justification

1. Penggunaan Azure Container Apps daripada Azure Kubernetes Service \
   Manfaat yang diperoleh:
   - Tanpa beban pengelolaan kluster Kubernetes (tidak ada kumpulan node, tidak memerlukan keahlian kubectl)
   - Penskalaan HTTP otomatis berbasis KEDA tanpa konfigurasi Prometheus/HPA
   - Kemampuan “scale-to-zero” menghilangkan biaya node yang tidak aktif — pool node minimum AKS selalu menimbulkan biaya komputasi bahkan saat lalu lintas nol
   - Waktu ke produksi yang lebih cepat bagi tim tanpa keahlian Kubernetes yang mendalam

   Apa yang dikorbankan:
   - Tidak dapat menjalankan beban kerja berstatus (stateful) yang memerlukan volume penyimpanan khusus
   - Kontrol jaringan yang kurang granular (tidak ada plugin CNI khusus)
   - Tidak dapat menerapkan operator Kubernetes atau CRD

   Kesimpulan: Dengan 50k month active user dan 5k peak user, abstraksi terkelola ACA memberikan ROI yang lebih baik. AKS akan dipertimbangkan kembali jika platform berkembang menjadi SaaS multi-tenant dengan 10+ layanan mikro yang memerlukan kemampuan platform lintas bidang.

2. Azure SQL Database daripada Cosmos DB \
   Apa yang diperoleh:
   - Dukungan transaksi ACID penuh untuk alur kerja pemesanan + penjadwalan ulang (F2) — sangat penting untuk menghindari pemesanan ganda
   - Kueri JOIN kompleks untuk dasbor analitik dealer (F7) tanpa perakitan data di sisi aplikasi
   - Perangkat SQL yang sudah dikenal oleh tim pengembangan
   - Biaya lebih rendah pada skala data ini dibandingkan dengan throughput yang disediakan oleh Cosmos DB

   Apa yang dikorbankan:
   - Skalabilitas horizontal terbatas — SQL berskala vertikal (vCores), bukan horizontal melintasi shard
   - Perubahan skema memerlukan migrasi, bukan evolusi dokumen tanpa skema
   - Penulisan multi-region tidak didukung secara native (replika geografis hanya baca)

   Kesimpulan: Model data inti portal ini pada dasarnya bersifat relasional (pengguna, janji temu, dealer, peringkat dengan hubungan kunci asing). Fleksibilitas multi-model Cosmos DB akan menjadi rekayasa berlebihan untuk kasus penggunaan ini. Jika metadata foto atau telemetri dealer yang tidak terstruktur tumbuh secara signifikan, Cosmos DB dapat diperkenalkan bersama SQL sebagai penyimpanan sekunder yang dirancang khusus.

3. Azure Front Door yang All-in-One \
   Manfaat yang diperoleh:
   - Platform kontrol tunggal untuk perutean, aturan WAF, penyimpanan cache CDN, dan DDoS — mengurangi risiko operasional
   - Penagihan terpadu dan SLA dari satu layanan
   - Dukungan Private Link bawaan ke asal ACA (tanpa IP publik di lapisan komputasi)
   - Termasuk perlindungan terhadap bot dan umpan Microsoft Threat Intelligence

   Apa yang dikorbankan:
   - Biaya dasar lebih tinggi ($180/bulan) dibandingkan CDN saja (~$85/bulan) untuk pengiriman statis sederhana
   - Front Door adalah sumber daya global — tidak dapat dibatasi ke region Southeast Asia untuk tujuan kepatuhan (metadata mungkin disimpan di luar Indonesia)
   - Penyesuaian aturan WAF yang kurang terperinci dibandingkan dengan penerapan Application Gateway WAF v2 khusus

   Kesimpulan: Untuk portal yang berhadapan dengan pelanggan yang membutuhkan WAF + CDN + penyeimbangan beban global secara bersamaan, konsolidasi Front Door Premium mengurangi kompleksitas operasional cukup untuk membenarkan biaya premiumnya. Jika persyaratan regulasi Indonesia berkembang hingga melarang metadata apa pun meninggalkan negara, Application Gateway WAF yang diterapkan di dalam VNet Asia Tenggara akan menggantikan Front Door.
