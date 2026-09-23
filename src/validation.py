import pandera as pa
import pandas as pd
import logging
from pandera import Column, DataFrameSchema, Check

logger = logging.getLogger(__name__)

SCHEMAS = {
    "orders": DataFrameSchema(
        {
            "order_id": Column(str, Check.str_length(min_value=1), nullable=False, unique=True),
            "customer_id": Column(str, Check.str_length(min_value=1), nullable=False),
            "order_status": Column(
                str,
                Check.isin([
                    "delivered", "shipped", "canceled", "unavailable",
                    "invoiced", "processing", "created", "approved",
                ]),
                nullable=False,
            ),
            "order_purchase_timestamp": Column("datetime64[ns]", nullable=False),
            "delivery_days": Column("Int64", Check.ge(0), nullable=True),
            "is_late": Column("Int64", Check.isin([0, 1]), nullable=True),
        },
        strict=False,
        coerce=True,
    ),
    "order_items": DataFrameSchema(
        {
            "order_id": Column(str, nullable=False),
            "order_item_id": Column("Int64", Check.ge(1), nullable=False),
            "price": Column(float, Check.ge(0), nullable=False),
            "freight_value": Column(float, Check.ge(0), nullable=False),
        },
        strict=False,
        coerce=True,
    ),
    "customers": DataFrameSchema(
        {
            "customer_id": Column(str, nullable=False, unique=True),
            "customer_unique_id": Column(str, nullable=False),
        },
        strict=False,
        coerce=True,
    ),
}


def validate_dataframe(df: pd.DataFrame, table_name: str) -> pd.DataFrame:
    """Waliduje DataFrame za pomocą schematu Pandera."""
    if table_name not in SCHEMAS:
        logger.warning(f"Brak schematu walidacyjnego dla tabeli: {table_name}. Pomijam walidację.")
        return df

    logger.info(f"Walidacja tabeli: {table_name}")

    try:
        validated_df = SCHEMAS[table_name].validate(df, lazy=True)
        logger.info(f"Walidacja zakończona pomyślnie dla: {table_name}")
        return validated_df
    except pa.errors.SchemaErrors as e:
        logger.error(f"Walidacja nie powiodła się dla {table_name}:")
        logger.error(f"Liczba błędów: {len(e.failure_cases)}")
        logger.error(f"Przykłady błędów:\n{e.failure_cases.head(10)}")
        raise