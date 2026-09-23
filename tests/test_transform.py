import pytest
import pandas as pd
from src.transform import transform_orders


class TestTransformOrders:

    def test_removes_duplicates(self, sample_orders_raw):
        result = transform_orders(sample_orders_raw)
        assert len(result) == 3
        assert set(result["order_id"]) == {"order_1", "order_2", "order_3"}

    def test_adds_is_late_column(self, sample_orders_raw):
        result = transform_orders(sample_orders_raw)
        assert "is_late" in result.columns
        assert result.loc[result["order_id"] == "order_3", "is_late"].iloc[0] == 0

    def test_adds_delivery_days_column(self, sample_orders_raw):
        result = transform_orders(sample_orders_raw)
        assert "delivery_days" in result.columns
        assert result.loc[result["order_id"] == "order_1", "delivery_days"].iloc[0] == 4

    def test_converts_timestamps_to_datetime(self, sample_orders_raw):
        result = transform_orders(sample_orders_raw)
        assert pd.api.types.is_datetime64_any_dtype(result["order_purchase_timestamp"])