# SOP IT Service Desk — Mitsubishi Indonesia Group
**Dokumen Internal · Versi 1.0 · 2025**

> Panduan standar untuk agen helpdesk dalam menangani tiket harian dari seluruh anak perusahaan Mitsubishi Indonesia. Dokumen ini mencakup 6 kategori dengan 12 prosedur — dari password reset, VPN, ERP, hingga permintaan hardware.

---

## Daftar Isi

- [SOP-001 — Manajemen Akses & Autentikasi](#sop-001--manajemen-akses--autentikasi)
- [SOP-002 — Konektivitas Jaringan & VPN](#sop-002--konektivitas-jaringan--vpn)
- [SOP-003 — Prosedur Perangkat Keras](#sop-003--prosedur-perangkat-keras)
- [SOP-004 — Sistem ERP SAP](#sop-004--sistem-erp-sap)
- [SOP-005 — Email & Office 365](#sop-005--email--office-365)
- [SOP-006 — Layanan Umum & Kebijakan](#sop-006--layanan-umum--kebijakan)

---

## SOP-001 — Manajemen Akses & Autentikasi
`Kategori: Access`

### 001.1 · Reset Password Domain Windows

Jika karyawan lupa password akun domain Windows, arahkan ke portal self-service terlebih dahulu sebelum eskalasi ke helpdesk.

**Prosedur:**

1. Arahkan karyawan ke portal self-service: `https://password-reset.bsi.id`
2. **Jika akun terkunci (Lockout):** Verifikasi identitas penelepon dengan meminta **NIK (Nomor Induk Karyawan)** sebelum melanjutkan
3. Setelah NIK terverifikasi, buka console **Active Directory** dan lakukan *unlock* akun pengguna
4. Infokan karyawan bahwa akun sudah terbuka, dan minta mereka segera mengganti password

> ⚠️ **Peringatan:** Dilarang keras melakukan unlock atau reset password tanpa verifikasi NIK terlebih dahulu. Ini adalah kontrol keamanan wajib.

---

### 001.2 · Reset Token MFA (Multi-Factor Authentication)

Berlaku jika karyawan mengganti smartphone baru atau token MFA mengalami kegagalan sinkronisasi. Prosedur ini dilakukan secara mandiri oleh karyawan.

**Prosedur:**

1. Karyawan login ke portal MyBSI-ID via **browser laptop**: `https://my.bsi.mitsubishi.com/mfa`
2. Masukkan **password utama Windows** untuk autentikasi portal
3. Pilih menu **"Revoke Token"** pada dashboard — token lama akan dinonaktifkan
4. Buka aplikasi **Microsoft Authenticator** di smartphone baru → pilih `Add Account` → `Work or School`
5. Scan **QR Code baru** yang muncul di layar portal untuk menyelesaikan pendaftaran

> ⚠️ **Catatan:** Karyawan **harus menggunakan browser laptop** (bukan mobile). Jika laptop tidak dapat diakses karena MFA belum aktif di perangkat lama, eskalasi ke Tier 2.

---

## SOP-002 — Konektivitas Jaringan & VPN
`Kategori: Network`

### 002.1 · Troubleshooting GlobalProtect VPN

Berlaku untuk karyawan yang mengalami error koneksi GlobalProtect saat bekerja dari rumah (WFH) atau lokasi remote.

**Prosedur:**

1. Pastikan koneksi internet ISP rumah stabil — minta karyawan coba akses situs publik (misal: `google.com`)
2. Buka aplikasi **GlobalProtect** di system tray → klik ikon gir **Settings** → pilih **Sign Out**
3. Lakukan **restart penuh** pada laptop/komputer karyawan
4. Setelah restart, login kembali dengan portal gateway: `vpn.bsi.mitsubishi.com`
5. **Jika muncul pesan "Gateway Not Responding":** Agen helpdesk melakukan *force reset* sesi VPN pengguna dari dashboard **Palo Alto Firewall**, lalu minta karyawan reconnect setelah 2–3 menit

> ⚠️ **Peringatan:** Reset sesi VPN via Palo Alto hanya dilakukan oleh agen helpdesk yang memiliki akses. Jangan berikan akses dashboard firewall kepada end-user.

---

### 002.2 · Akses Wi-Fi BSI-Guest (Tamu & Vendor)

Tamu atau vendor yang berkunjung ke kantor cabang **hanya diperbolehkan menggunakan jaringan BSI-Guest**. Jaringan ini terpisah dari jaringan internal perusahaan.

**Informasi Penting:**

- Password BSI-Guest dirotasi otomatis setiap **Senin pukul 08:00 WIB** oleh sistem
- Karyawan yang mengundang tamu dapat melihat password guest harian pada **layar monitor di area resepsionis**
- Jika tamu tidak dapat menemukan password, arahkan ke **petugas resepsionis**

> ℹ️ Helpdesk **tidak mendistribusikan** password guest melalui telepon atau email.

---

## SOP-003 — Prosedur Perangkat Keras
`Kategori: Hardware`

### 003.1 · Pengajuan Laptop Pengganti (Device Refresh)

**Syarat:** Karyawan berhak mengajukan laptop pengganti apabila usia laptop saat ini sudah **melebihi 4 tahun**.

**Prosedur:**

1. Karyawan mengisi form pengajuan *refresh device* di portal **IT Service Management (ITSM)**, sertakan serial number laptop lama
2. Tiket membutuhkan **approval digital dari Manajer Departemen (Tier 1)** — sistem ITSM akan otomatis mengirim notifikasi ke manajer
3. Setelah disetujui, **IT Asset Management** menyiapkan perangkat baru dan melakukan imajing/konfigurasi awal

**SLA:** Penyediaan perangkat **3 hari kerja** setelah approval manajer diterima

> ⚠️ Tiket tanpa approval manajer tidak akan diproses. Arahkan karyawan untuk follow-up ke manajernya jika approval tertunda lebih dari 2 hari kerja.

---

### 003.2 · Permintaan Peripheral Tambahan

Permintaan perangkat keras peripheral (monitor tambahan, mouse nirkabel, keyboard mekanik, dll.) harus melalui prosedur berikut:

**Prosedur:**

1. Karyawan membuat tiket ITSM dan mencantumkan **alasan bisnis (business justification)** yang jelas dan spesifik
2. Tiket wajib mendapat **approval atasan langsung** sebelum dapat diproses oleh IT
3. Setelah disetujui, IT akan memproses pengadaan atau pengambilan dari stok IT Asset

**Contoh justifikasi yang valid:**
> "Kebutuhan monitor kedua untuk anggota tim data analyst / desain grafis guna meningkatkan efisiensi kerja multi-layar."

**Contoh justifikasi yang tidak valid:**
> "Minta mouse baru." / "Monitor lama kurang nyaman." — tanpa konteks kebutuhan bisnis yang spesifik.

---

## SOP-004 — Sistem ERP SAP
`Kategori: ERP`

### 004.1 · Error SAP GUI: WSAECONNREFUSED

Error `WSAECONNREFUSED: Connection refused` pada SAP GUI biasanya disebabkan VPN tidak aktif atau konfigurasi IP server salah.

**Prosedur:**

1. **Cek status VPN:** Jika karyawan berada di luar jaringan kantor, pastikan GlobalProtect aktif dan terhubung ke `vpn.bsi.mitsubishi.com`
2. Arahkan karyawan untuk membuka file konfigurasi SAP Logon: `saplogon.ini`
3. Verifikasi kolom **Application Server** sudah diarahkan ke IP yang benar: `10.50.100.12`
4. Jika konfigurasi sudah benar namun masih gagal, periksa apakah IP karyawan **terkena blokir firewall ERP** — koordinasikan dengan tim Network jika diperlukan

> ℹ️ **Referensi cepat:** IP SAP Application Server yang benar adalah `10.50.100.12`

---

### 004.2 · Akun SAP Terkunci (Account Locked)

Sistem SAP otomatis mengunci akun pengguna yang **tidak aktif selama 90 hari**. Agen Tier 1 **tidak memiliki akses** untuk membuka kunci ini.

**Prosedur:**

1. Konfirmasi kepada karyawan bahwa akun SAP-nya terkunci karena inaktivitas 90 hari
2. **Eskalasi tiket** ke grup `SAP Basis Team` melalui portal ITSM. Sertakan:
   - Nama karyawan & NIK
   - SAP User ID
   - Tanggal terakhir login (jika diketahui)
3. Informasikan kepada karyawan bahwa proses *unlock* membutuhkan waktu **maksimal 1×24 jam**

> 🔺 **Eskalasi ke:** SAP Basis Team | **SLA:** Maks. 1×24 jam

---

## SOP-005 — Email & Office 365
`Kategori: Software/Access`

### 005.1 · Mailbox Outlook Penuh (Quota Exceeded)

Batas penyimpanan mailbox standar untuk karyawan reguler adalah **50 GB**.

**Prosedur:**

1. Arahkan karyawan untuk membuka Outlook dan **menghapus email lama** yang memiliki attachment berukuran besar (gunakan filter: *Sort by Size*)
2. Aktifkan fitur **Online Archive** di Outlook untuk memindahkan email berusia lebih dari 1 tahun ke arsip cloud secara otomatis
3. Jika karyawan membutuhkan upgrade kuota di atas 50 GB, diperlukan **persetujuan Head of IT** — hanya untuk level Direktur atau kasus khusus

> ⚠️ Helpdesk Tier 1 **tidak dapat langsung menambah kuota**. Permintaan upgrade harus melalui persetujuan Head of IT sebelum dieksekusi oleh tim Microsoft 365.

---

### 005.2 · Permintaan Lisensi Microsoft Visio / Project

Microsoft Visio dan Project **bukan bagian dari lisensi Office 365 E3 standar**. Karyawan harus mengajukan permintaan khusus.

**Prosedur:**

1. Karyawan membuat **tiket permohonan software** di portal ITSM, dilengkapi alasan kebutuhan bisnis
2. Lampirkan **persetujuan Manajer Departemen** (screenshot email atau approval digital di ITSM)
3. **IT Procurement** memproses pembelian lisensi dan melakukan *charge-back* biaya ke **cost-center departemen** yang bersangkutan

> ℹ️ **Penting:** Biaya lisensi Visio/Project dibebankan ke anggaran departemen pemohon, bukan ke anggaran IT. Pastikan karyawan sudah menginformasikan hal ini ke manajer/finance departemennya.

---

## SOP-006 — Layanan Umum & Kebijakan
`Kategori: Other`

> ⚠️ **Perhatian Agen:** SOP ini mendefinisikan batas ruang lingkup IT Service Desk. Permintaan di luar cakupan ini harus diarahkan ke departemen yang tepat — **jangan tangani sendiri**.

---

### 006.1 · Pemesanan Ruang Rapat & Konsumsi

**❌ Di luar cakupan IT Service Desk**

Keluhan atau permintaan terkait pemesanan ruang rapat, ketersediaan proyektor di ruang rapat, dan pemesanan konsumsi meeting **bukan ranah IT**.

**Arahkan karyawan ke:**

- **BSI Facility Booking** — sistem reservasi online (dapat diakses melalui intranet perusahaan)
- **General Affairs (GA)** — via telepon meja di ekstensi `101`

---

### 006.2 · Penggantian ID Card Hilang / Rusak

**❌ Di luar cakupan IT Service Desk**

Penggantian fisik ID Card (Kartu Akses Gedung) yang hilang atau rusak **bukan tanggung jawab IT**.

**Arahkan karyawan ke:**

1. Tim **HR (Human Resources)** — untuk pencatatan dan prosedur administrasi
2. **Security Gedung di Lantai 1** — untuk pencetakan ulang kartu akses fisik

**Peran IT dalam kasus ini:** IT *hanya* bertugas melakukan sinkronisasi data dari HRIS ke sistem akses pintu (door access) **setelah** kartu fisik baru diterbitkan oleh HR. Tidak ada tindakan IT sebelum kartu baru tersedia.

---

*IT Service Desk — Mitsubishi Indonesia Group · Dokumen Internal · Versi 1.0 · 2025*
