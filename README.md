# Dokumentacja projektu – Konteneryzacja i orkiestracja usług IT
**Autor:** Marcin Łagódka  
**Data:** 06.02.2026  

---

## 1. Cel i zakres
Projekt przygotowuje spójne środowisko wielokontenerowe spełniające wymagania zaliczenia: baza danych, aplikacja korzystająca z DB, co najmniej jedna usługa dostępna przez przeglądarkę, konfiguracja w `docker-compose.yml` oraz dokumentacja. 

W skład wchodzi: **MariaDB**, **aplikacja web python**, **Adminer**, **Grafana**, **Nginx (docs)**, **Caddy (reverse proxy + TLS internal)**.

---

## 2. Architektura
Poniżej znajduje się diagram architektury (PNG) oraz wariant w Mermaid (do podglądu na GitHub/VS Code).

### 2.1 Diagram (PNG)
![Diagram architektury](diagram-architektury.png)

### 2.2 Diagram (Mermaid)
```mermaid
flowchart LR
    subgraph Internet[Przeglądarka lokalna]
    end

    Internet -->|HTTPS| Caddy

    subgraph Sieć web
    Caddy
    App[app (8000)]
    MariaDB[(MariaDB)]
    Adminer[Adminer (8080)]
    NginxDoc[Nginx doc (80)]
    Grafana[Grafana (3000)]
    end

    Caddy --> Adminer
    Caddy --> Grafana
    Caddy --> NginxDoc
    Caddy --> App

    App <--> MariaDB