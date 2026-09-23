import pandas as pd
import logging
from pathlib import Path
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Błąd podczas ekstrakcji danych."""
    pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((pd.errors.ParserError, IOError)),
    reraise=True,
)
def _read_csv_with_retry(filepath: Path) -> pd.DataFrame:
    """Czyta CSV z ponownymi próbami w przypadku błędów przejściowych."""
    logger.debug(f"Próba odczytu pliku: {filepath}")
    return pd.read_csv(filepath)


def extract_table(table_name: str, file_path: Path) -> pd.DataFrame:
    """Ekstrahuje pojedynczą tabelę z pliku CSV."""
    logger.info(f"Ekstrakcja tabeli: {table_name} z {file_path}")

    if not file_path.exists():
        msg = f"Plik nie istnieje: {file_path}"
        logger.error(msg)
        raise ExtractionError(msg)

    try:
        df = _read_csv_with_retry(file_path)
        logger.info(
            f"Pomyślnie wczytano {table_name}: {len(df):,} wierszy, {len(df.columns)} kolumn"
        )
        return df
    except pd.errors.EmptyDataError as e:
        logger.error(f"Plik jest pusty: {file_path}")
        raise ExtractionError(f"Plik jest pusty: {file_path}") from e
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd podczas czytania {file_path}: {e}")
        raise ExtractionError(f"Błąd czytania {file_path}: {e}") from e