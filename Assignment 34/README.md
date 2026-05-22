flowchart TD

    U["User Mobile / Web (Indonesia)"]
    FD["Azure Front Door Premium\nWAF + CDN + DDoS"]
    CDN["Azure CDN\nStatic Assets"]
    subgraph COMPUTE["Compute Tier (Primary: Jakarta)"]
    ACA["Azure Container Apps\n(API Gateway, Booking, Rating, Analytics)"]
    FUNC["Azure Functions\n(Async: Upload, Notifications)"]
    end

    subgraph DATA["Data Tier"]
    SQL["Azure SQL DB\nBusiness Critical\nGeo-replication → East Asia"]
    REDIS["Azure Cache for Redis\n(Session, Scheduling)"]
    BLOB["Azure Blob Storage\n(Photos, Files)"]
    end

    subgraph MSG["Messaging & Notification"]
    SB["Azure Service Bus\n(Queue)"]
    HUB["Notification Hubs\n(Push)"]
    ACS["Azure Communication Services\n(SMS, Email)"]
    end

    subgraph ID["Identity & Security"]
    ENTRA[Microsoft Entra External ID]
    KV[Azure Key Vault]
    RBAC[RBAC Roles]
    end

    subgraph OBS["Observability"]
    APPINSIGHTS[Application Insights]
    LOG[Log Analytics]
    MONITOR[Azure Monitor + Alerts]
    end

    %% FLOW
    U --> FD
    FD --> CDN
    FD --> ACA

    CDN --> BLOB

    ACA --> SQL
    ACA --> REDIS
    ACA --> BLOB

    ACA --> SB
    SB --> FUNC

    FUNC --> HUB
    FUNC --> ACS

    ACA --> ENTRA
    ACA --> KV
    ACA --> RBAC

    ACA --> APPINSIGHTS
    FUNC --> APPINSIGHTS

    APPINSIGHTS --> LOG
    LOG --> MONITOR

---

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

- Ada integrasi user dan manajemen profil
- Bisa booking dan reschedule servis
- Upload photo
- Notif real-time
- scheduler management pada sisi dealer
- Post-service rating dan feedback
- Management analytics dashboard
- Integrasi dengan sistem dealer yang sudah ada

b. Non fungsional

- Availability >= 99.95%
- P95 page load kurang dari 2s
- Auto-scaling untuk peak 5k user
- enkripsi pada REST dan saat transit
- ada daily backup dengan retensi data selama 30 hari
- RTO kurang dari 4 jam dan RPO kurang dari 1 jam
- Mengikuti undang-undang data residency
- monitoring dan alerting central

---

Answer:
Pada saat pembuatan aplikasi
