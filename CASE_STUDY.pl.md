# Case Study: Pipeline danych dla e-commerce

**Projekt:** End-to-End ETL Pipeline z Pythonem i PostgreSQL
**Czas realizacji:** 3 dni (projekt, implementacja, testy)
**Rola:** Data Engineer (samodzielnie)
**Stos:** Python, Pandas, PostgreSQL, Docker, Pandera, pytest

---

## Problem

Firma e-commerce przechowuje dane operacyjne w 9 osobnych plikach CSV,
eksportowanych z różnych systemów — zamówienia, klienci, produkty, płatności,
opinie, sprzedawcy i logistyka.

**Problemy:**

- **Brak jednego źródła prawdy.** Żeby odpowiedzieć na proste pytanie typu
  *„ile wyniósł przychód w zeszłym miesiącu?"*, analityk musiał ręcznie otwierać
  kilka plików i łączyć je w Excelu.
- **Niespójna jakość danych.** Duplikaty, brakujące wartości, ujemne ceny,
  różne formaty dat między plikami.
- **Brak walidacji.** Nic nie powstrzymywało błędnych rekordów przed trafieniem
  do raportów.
- **Wolny, ręczny proces.** Każdy raport oznaczał godziny ręcznej pracy.

Firma potrzebowała niezawodnego, zautomatyzowanego sposobu przenoszenia danych
do bazy, w której można je przeszukiwać w kilka sekund.

---

## Rozwiązanie

Zaprojektowałam i zbudowałam pipeline ETL, który:

1. **Pobiera** wszystkie 9 plików CSV z automatycznymi ponowieniami przy błędach.
2. **Przetwarza** dane — usuwa duplikaty, konwertuje typy, parsuje daty,
   dodaje kolumny pochodne (czas dostawy, flaga opóźnienia).
3. **Waliduje** każdą tabelę względem schematu Pandera przed załadowaniem.
4. **Ładuje** oczyszczone dane do PostgreSQL przez protokół `COPY` —
   8 razy szybciej niż standardowe `to_sql`.
5. **Udostępnia** dane przez zapytania SQL do analityki.

Wszystko działa w Dockerze, konfiguracja w YAML, logi z rotacją,
testy jednostkowe uruchamiane automatycznie przez GitHub Actions.

---

## Efekt

| Metryka | Wartość |
|---|---|
| Przetworzone tabele | 9 |
| Załadowane wiersze | 1 551 822 |
| Czas działania pipeline'u | ~40 sekund |
| Przyspieszenie ładowania | 8x (COPY vs to_sql) |
| Pokrycie testami | Kluczowa logika transformacji |
| Reprodukowalność | Jedno `docker compose up` |

**Co to oznacza dla biznesu:**

- Analitycy odpowiadają na pytania w **sekundach**, nie godzinach.
- Jakość danych jest **wymuszona** — błędne rekordy są odrzucane zanim trafią do bazy.
- Pipeline działa **powtarzalnie** — koniec z ręczną obsługą CSV.
- Dodanie nowego źródła danych zajmuje **minuty**, nie dni.

---

## Kluczowe rozwiązania techniczne

- **Modularny design:** extract, transform, load — każdy krok osobno i testowalny.
- **Walidacja na wejściu:** schematy Pandera wychwytują błędy typów, nieprawidłowe
  wartości i dane poza zakresem, zanim trafią do bazy.
- **Wydajność:** PostgreSQL `COPY FROM STDIN` strumieniuje dane bezpośrednio do
  bazy zamiast wysyłać 1,5 miliona pojedynczych INSERT-ów.
- **Obsługa błędów:** ponowienia z wykładniczym backoffem dla błędów przejściowych.
- **Obserwowalność:** strukturalne logi do konsoli i pliku z rotacją.
- **Reprodukowalność:** Docker zapewnia identyczne działanie na każdej maszynie.

---

## Co dalej

- Dodać **Airflow** do harmonogramowania pipeline'u codziennie.
- Dodać **dbt** dla wersjonowanych transformacji SQL.
- Podłączyć **narzędzie BI** (Metabase, Superset) dla dashboardów self-service.
- Rozszerzyć pipeline o pobieranie danych z **REST API**, nie tylko z CSV.

---

## Linki

- **Repozytorium:** [github.com/anna1sheludko/end-to-end-pipeline](https://github.com/anna1sheludko/end-to-end-pipeline)
- **Kontakt:** annasheludko152@gmail.com