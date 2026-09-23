# Case Study: E-Commerce Data Pipeline

**Project:** End-to-End ETL Pipeline with Python and PostgreSQL
**Timeline:** 3 days (design, implementation, testing)
**Role:** Data Engineer (solo)
**Stack:** Python, Pandas, PostgreSQL, Docker, Pandera, pytest

---

## The Problem

An e-commerce business stores its operational data in 9 separate CSV files
exported from different systems — orders, customers, products, payments,
reviews, sellers, and logistics.

**The issues:**

- **No single source of truth.** To answer a simple question like *"what was our
  revenue last month?"*, an analyst had to manually open several files and join
  them in Excel.
- **Inconsistent data quality.** Duplicate rows, missing values, negative prices,
  and inconsistent date formats across files.
- **No validation.** Nothing stopped broken records from reaching reports.
- **Slow, manual process.** Every report meant hours of manual preparation.

The business needed a reliable, automated way to move this data into a database
where it could be queried in seconds.

---

## The Solution

I designed and built an end-to-end ETL pipeline that:

1. **Extracts** all 9 CSV files with automatic retries on transient errors.
2. **Transforms** the data — removing duplicates, casting types, parsing dates,
   and adding derived columns (delivery time, late-delivery flag).
3. **Validates** every table against a Pandera schema before loading.
4. **Loads** the cleaned data into PostgreSQL using the `COPY` protocol — 
   8x faster than the standard `to_sql` method.
5. **Exposes** the data through SQL queries for analytics.

Everything runs in Docker, is configured in YAML, logs every step with rotation,
and is covered by unit tests that run automatically on GitHub Actions.

---

## The Result

| Metric | Value |
|---|---|
| Tables processed | 9 |
| Rows loaded | 1,551,822 |
| Pipeline runtime | ~40 seconds |
| Load speed improvement | 8x (COPY vs to_sql) |
| Test coverage | Core transform logic |
| Reproducibility | One `docker compose up` |

**What this means for the business:**

- Analysts can now answer questions in **seconds**, not hours.
- Data quality is **enforced** — bad records are rejected before they reach the database.
- The pipeline runs **repeatably** — no more manual CSV handling.
- Adding a new data source takes **minutes**, not days.

---

## Technical Highlights

- **Modular design:** extract, transform, load — each step isolated and testable.
- **Validation-first:** Pandera schemas catch type errors, invalid values, and
  out-of-range data before loading.
- **Performance:** PostgreSQL `COPY FROM STDIN` streams data directly into the
  database instead of issuing 1.5 million individual INSERT statements.
- **Error handling:** retries with exponential backoff for transient failures.
- **Observability:** structured logging to both console and rotating files.
- **Reproducibility:** Docker ensures the pipeline runs identically on any machine.

---

## What I Would Do Next

- Add **Airflow** to schedule the pipeline daily.
- Add **dbt** for versioned SQL transformations.
- Connect a **BI tool** (Metabase, Superset) for self-service dashboards.
- Extend the pipeline to consume data from **REST APIs**, not only CSV files.

---

## Links

- **Repository:** [github.com/anna1sheludko/end-to-end-pipeline](https://github.com/anna1sheludko/end-to-end-pipeline)
- **Contact:** annasheludko152@gmail.com