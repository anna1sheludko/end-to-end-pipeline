# Etap 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Kopiuj requirements i zainstaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Etap 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Instalacja tylko bibliotek runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Skopiuj zainstalowane pakiety z buildera
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Skopiuj kod aplikacji
COPY src/ ./src/
COPY config/ ./config/
COPY sql/ ./sql/

# Domyślna komenda
CMD ["python", "-m", "src.cli"]
