# End-to-End ETL Pipeline — Python i PostgreSQL

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-✓-blue?logo=docker)
![Pandas](https://img.shields.io/badge/Pandas-2.2-blue?logo=pandas)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

Gotowy do wdrożenia pipeline ETL, który pobiera dane e-commerce z plików CSV,
waliduje je i przetwarza w Pandas + Pandera, a następnie ładuje do PostgreSQL
z wykorzystaniem szybkiego protokołu `COPY`.

Projekt portfolio pokazujący praktyki stosowane w prawdziwych zespołach danych:
modularny kod, walidacja danych, obsługa błędów z ponowieniami, strukturalne
logowanie, testy jednostkowe i pełna reprodukowalność dzięki Dockerowi.

> 🇬🇧 English version: [README.md](README.md)

---

## Jaki problem rozwiązuje ten projekt?

Dane e-commerce są rozproszone po wielu plikach CSV i pełne duplikatów, braków
oraz niespójnych typów. Analityk nie jest w stanie szybko odpowiedzieć na pytania:

- Ile wyniósł przychód w danym miesiącu?
- Które kategorie produktów sprzedają się najlepiej?
- Jaki jest średni czas dostawy w poszczególnych regionach?

Pipeline automatyzuje cały proces: pobiera dane, czyści je, waliduje względem
schematów, ładuje do relacyjnej bazy i udostępnia je do analizy SQL.

---

## Architektura

![Diagram architektury](docs/architecture.png)

```
┌─────────────────┐
│  CSV (Kaggle)   │  ← 9 plików, ~1,5 mln wierszy
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  EXTRACT        │  Pandas: read_csv z ponowieniami
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  TRANSFORM      │  Czyszczenie: deduplikacja, typy, daty
│  + VALIDATION   │  Pandera: walidacja schematu i reguł biznesowych
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LOAD           │  psycopg2 COPY (8x szybciej niż to_sql)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL 15  │  Model relacyjny z kluczami obcymi i indeksami
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQL Analytics  │  Przychody, dostawy, opinie klientów
└─────────────────┘
```

---

## Stos technologiczny

| Narzędzie | Zastosowanie |
|---|---|
| **Python 3.12** | Język główny |
| **Pandas** | Przetwarzanie danych |
| **Pandera** | Walidacja schematów |
| **psycopg2** | Sterownik PostgreSQL |
| **PostgreSQL 15** | Docelowa hurtownia danych |
| **Docker & Compose** | Reprodukowalność środowiska |
| **Tenacity** | Ponowienia przy błędach przejściowych |
| **pytest** | Testy jednostkowe |
| **PyYAML** | Konfiguracja deklaratywna |
| **python-dotenv** | Zarządzanie sekretami |
| **GitHub Actions** | CI/CD |

---

## Struktura projektu

```
end-to-end-pipeline/
├── .github/workflows/       # GitHub Actions (automatyczne testy)
├── config/
│   └── config.yaml          # Konfiguracja tabel
├── data/raw/                # Pliki źródłowe CSV (poza repo)
├── docs/                    # Diagramy, screeny
├── logs/                    # Logi z rotacją (poza repo)
├── sql/
│   ├── 01_init_schema.sql   # DDL: tabele, klucze, indeksy
│   └── 02_analytics.sql     # Zapytania analityczne
├── src/
│   ├── cli.py               # Interfejs CLI (argparse)
│   ├── config_loader.py     # Ładowanie YAML + .env
│   ├── extract.py           # Krok EXTRACT z ponowieniami
│   ├── transform.py         # Krok TRANSFORM (czyszczenie)
│   ├── validation.py        # Schematy Pandera
│   ├── load.py              # Krok LOAD (COPY do PostgreSQL)
│   ├── pipeline.py          # Orkiestracja
│   └── logging_config.py    # Strukturalne logowanie
├── tests/
│   ├── conftest.py          # Fixtury pytest
│   └── test_transform.py    # Testy jednostkowe
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.pl.md
```

---

## Jak uruchomić

### Wymagania

- Python 3.12+
- Docker Desktop
- Git

### 1. Sklonuj repozytorium

```bash
git clone https://github.com/anna1sheludko/end-to-end-pipeline.git
cd end-to-end-pipeline
```

### 2. Pobierz dane

Pobierz [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
i umieść wszystkie 9 plików CSV w katalogu `data/raw/`.

### 3. Skonfiguruj środowisko

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Zmienne środowiskowe

```bash
cp .env.example .env
# Uzupełnij .env swoimi danymi dostępowymi
```

> **Uwaga:** projekt używa portu **5433** dla PostgreSQL, żeby uniknąć konfliktu
> z lokalnie zainstalowaną instancją (np. Odoo) na porcie 5432.

### 5. Uruchom PostgreSQL

```bash
docker compose up -d postgres
```

### 6. Zainicjalizuj schemat bazy

```bash
Get-Content sql/01_init_schema.sql | docker exec -i olist_postgres psql -U olist_user -d olist_db
```

### 7. Uruchom pipeline

```bash
python -m src.cli --log-level INFO
```

Albo pojedynczą tabelę:

```bash
python -m src.cli --table orders
```

### 8. Przeglądaj dane

```bash
docker exec -it olist_postgres psql -U olist_user -d olist_db
```

Następnie uruchom dowolne zapytanie z `sql/02_analytics.sql`.

---

## Przykładowe wyniki

### Załadowane tabele

![Tabele](docs/screenshots/01_tables_overview.png)

### Przychód miesięczny

![Przychód miesięczny](docs/screenshots/02_monthly_revenue.png)

### Top kategorie produktów

![Top kategorie](docs/screenshots/03_top_categories.png)

### Wydajność pipeline'u

- **9 tabel** załadowanych
- **1 551 822 wierszy** łącznie
- **~40 sekund** end-to-end
- **8x szybciej** dzięki `COPY` zamiast `to_sql`

---

## Testy

```bash
pytest tests/ -v
```

Testy jednostkowe pokrywają:

- Usuwanie duplikatów
- Konwersję typów dat
- Kolumny pochodne (`is_late`, `delivery_days`)

GitHub Actions uruchamia testy przy każdym pushu.

---

## Czego uczy ten projekt

- **Modularny design ETL** — osobne kroki extract / transform / load
- **Walidacja danych** — schematy Pandera z regułami biznesowymi
- **Obsługa błędów** — ponowienia przez Tenacity, własne wyjątki
- **Optymalizacja wydajności** — protokół `COPY` zamiast `to_sql`
- **Praktyki produkcyjne** — logowanie z rotacją, sekrety w `.env`
- **Konfiguracja** — YAML dla deklaratywnych ustawień
- **CLI** — argparse z podkomendami i flagami
- **Testowanie** — fixtury pytest, testy jednostkowe, CI
- **Reprodukowalność** — Docker dla bazy i aplikacji
- **Analityka SQL** — realne zapytania biznesowe, nie zabawki

---

## Licencja

MIT — szczegóły w pliku [LICENSE](LICENSE).

---

## Autorka

**Anna Sheludko**

- GitHub: [@anna1sheludko](https://github.com/anna1sheludko)
- Email: annasheludko152@gmail.com