import pandas as pd
import logging
import psycopg2
from io import StringIO
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    pass


class DatabaseConnection:
    def __init__(self, config: dict):
        self.config = config
        self.conn = None

    def __enter__(self):
        try:
            self.conn = psycopg2.connect(
                host=self.config["host"],
                port=self.config["port"],
                dbname=self.config["name"],
                user=self.config["user"],
                password=self.config["password"],
                connect_timeout=10,
            )
            logger.debug("Połączenie z bazą danych ustanowione.")
            return self
        except psycopg2.OperationalError as e:
            logger.error(f"Nie można połączyć się z bazą: {e}")
            raise DatabaseError(f"Błąd połączenia: {e}") from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()
            logger.debug("Połączenie z bazą zamknięte.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(psycopg2.OperationalError),
    )
    def truncate_table(self, table_name: str):
        with self.conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {table_name} CASCADE;")
            self.conn.commit()
        logger.info(f"Wyczyszczono tabelę: {table_name}")


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(psycopg2.OperationalError),
)
def load_table_with_copy(db: DatabaseConnection, df: pd.DataFrame, table_name: str):
    """Ładuje DataFrame do PostgreSQL za pomocą COPY (szybkie!)."""
    if df.empty:
        logger.warning(f"Tabela {table_name} jest pusta. Pomijam ładowanie.")
        return

    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False, sep="\t", na_rep="\\N", float_format="%g")
    buffer.seek(0)

    columns = ", ".join(df.columns)

    try:
        with db.conn.cursor() as cur:
            cur.copy_expert(
                f"COPY {table_name} ({columns}) FROM STDIN WITH (FORMAT CSV, DELIMITER '\t', NULL '\\N')",
                buffer,
            )
            db.conn.commit()
        logger.info(f"Załadowano {len(df):,} wierszy do {table_name} przez COPY")
    except psycopg2.Error as e:
        db.conn.rollback()
        logger.error(f"Błąd COPY dla {table_name}: {e}")
        raise DatabaseError(f"Błąd ładowania {table_name}: {e}") from e


def load_all(dataframes: dict, config: dict):
    tables_config = config["tables"]
    sorted_tables = sorted(tables_config.items(), key=lambda x: x[1]["load_order"])

    with DatabaseConnection(config["database"]) as db:
        for table_name, table_config in sorted_tables:
            if table_name not in dataframes:
                logger.warning(f"Brak danych dla tabeli: {table_name}. Pomijam.")
                continue

            df = dataframes[table_name]
            logger.info(f"Ładowanie tabeli: {table_name}")

            db.truncate_table(table_name)
            load_table_with_copy(db, df, table_name)

    logger.info("Ładowanie wszystkich tabel zakończone.")