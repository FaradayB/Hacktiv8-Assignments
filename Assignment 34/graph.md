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
