import pytest
import pandas as pd


@pytest.fixture
def sample_orders_raw():
    return pd.DataFrame({
        "order_id": ["order_1", "order_2", "order_2", "order_3"],
        "customer_id": ["cust_1", "cust_2", "cust_2", "cust_3"],
        "order_status": ["delivered", "delivered", "delivered", "shipped"],
        "order_purchase_timestamp": [
            "2017-01-01 10:00:00", "2017-01-02 11:00:00",
            "2017-01-02 11:00:00", "2017-01-03 12:00:00",
        ],
        "order_approved_at": [
            "2017-01-01 10:30:00", "2017-01-02 11:30:00",
            "2017-01-02 11:30:00", "2017-01-03 12:30:00",
        ],
        "order_delivered_carrier_date": [
            "2017-01-02 08:00:00", "2017-01-03 09:00:00",
            "2017-01-03 09:00:00", "2017-01-04 10:00:00",
        ],
        "order_delivered_customer_date": [
            "2017-01-05 14:00:00", "2017-01-06 15:00:00",
            "2017-01-06 15:00:00", "2017-01-07 16:00:00",
        ],
        "order_estimated_delivery_date": [
            "2017-01-06 00:00:00", "2017-01-07 00:00:00",
            "2017-01-07 00:00:00", "2017-01-08 00:00:00",
        ],
    })