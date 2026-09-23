import pandas as pd
import logging
from src.validation import validate_dataframe

logger = logging.getLogger(__name__)


def _parse_dates(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def _strip_strings(df: pd.DataFrame) -> pd.DataFrame:
    str_cols = df.select_dtypes(include=["object"]).columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": None, "": None})
    return df


def transform_orders(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Transformacja: orders")
    df = _strip_strings(df)

    date_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    df = _parse_dates(df, date_cols)

    before = len(df)
    df = df.drop_duplicates(subset=["order_id"])
    if len(df) < before:
        logger.info(f"Usunięto {before - len(df)} duplikatów z orders")

    df = df.dropna(subset=["order_id", "customer_id"])

    df["is_late"] = (
        df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]
    ).astype("Int64")
    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.days.astype("Int64")

    df = validate_dataframe(df, "orders")
    logger.info(f"Transformacja orders zakończona: {len(df):,} wierszy")
    return df


def transform_order_items(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Transformacja: order_items")
    df = _strip_strings(df)
    df = _parse_dates(df, ["shipping_limit_date"])

    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["freight_value"] = pd.to_numeric(df["freight_value"], errors="coerce")
    df["order_item_id"] = pd.to_numeric(df["order_item_id"], errors="coerce").astype("Int64")

    before = len(df)
    df = df[df["price"] >= 0]
    if len(df) < before:
        logger.info(f"Usunięto {before - len(df)} wierszy z ujemną ceną")

    df = df.drop_duplicates(subset=["order_id", "order_item_id"])
    df = validate_dataframe(df, "order_items")
    logger.info(f"Transformacja order_items zakończona: {len(df):,} wierszy")
    return df


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Transformacja: customers")
    df = _strip_strings(df)

    before = len(df)
    df = df.drop_duplicates(subset=["customer_id"])
    if len(df) < before:
        logger.info(f"Usunięto {before - len(df)} duplikatów z customers")

    df = df.dropna(subset=["customer_id"])
    df = validate_dataframe(df, "customers")
    logger.info(f"Transformacja customers zakończona: {len(df):,} wierszy")
    return df


def transform_products(df: pd.DataFrame) -> pd.DataFrame:
    """Transformacja tabeli products z konwersją kolumn numerycznych na Int64."""
    logger.info("Transformacja: products")
    df = _strip_strings(df)

    int_cols = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    df = df.drop_duplicates(subset=["product_id"])
    df = df.dropna(subset=["product_id"])
    logger.info(f"Transformacja products zakończona: {len(df):,} wierszy")
    return df


def transform_order_payments(df: pd.DataFrame) -> pd.DataFrame:
    """Transformacja tabeli order_payments."""
    logger.info("Transformacja: order_payments")
    df = _strip_strings(df)

    df["payment_sequential"] = pd.to_numeric(df["payment_sequential"], errors="coerce").astype("Int64")
    df["payment_installments"] = pd.to_numeric(df["payment_installments"], errors="coerce").astype("Int64")
    df["payment_value"] = pd.to_numeric(df["payment_value"], errors="coerce")

    df = df.drop_duplicates(subset=["order_id", "payment_sequential"])
    logger.info(f"Transformacja order_payments zakończona: {len(df):,} wierszy")
    return df


def transform_simple(df: pd.DataFrame, name: str) -> pd.DataFrame:
    """Ogólna transformacja dla prostych tabel."""
    logger.info(f"Transformacja: {name}")
    df = _strip_strings(df)
    return df


TRANSFORM_MAP = {
    "orders": transform_orders,
    "order_items": transform_order_items,
    "customers": transform_customers,
    "products": transform_products,
    "order_payments": transform_order_payments,
    "sellers": lambda df: transform_simple(df, "sellers"),
    "order_reviews": lambda df: transform_simple(df, "order_reviews"),
    "geolocation": lambda df: transform_simple(df, "geolocation"),
    "product_category_translation": lambda df: transform_simple(df, "product_category_translation"),
}