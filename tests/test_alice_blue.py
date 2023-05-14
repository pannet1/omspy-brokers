from omspy_brokers.alice_blue import *
import pytest
from unittest.mock import patch
import pendulum
import json


@pytest.fixture
def ab():
    with patch("pya3.Aliceblue") as alice:
        broker = AliceBlue(user_id="user_id", api_key="api_key")
        broker.alice = alice
        return broker


def test_ab_authenticate(ab):
    ab.authenticate()
    ab.alice.get_session_id.side_effect = ["session_id"] * 4
    ab.alice.get_session_id.assert_called_once()
    assert ab.authenticate() == "session_id"
    assert ab.alice.get_session_id() == "session_id"


def test_ab_orders(ab):
    ab.authenticate()
    with open("tests/data/alice_blue/orders.json") as f:
        dct = json.load(f)
        ab.alice.get_order_history.return_value = dct
    orders = ab.orders
    ab.alice.get_order_history.assert_called_once()
    assert len(orders) == 2
    keys_in = [
        "symbol",
        "average_price",
        "quantity",
        "filled_quantity",
        "order_id",
        "segment",
        "status",
        "cancelled_quantity",
    ]
    for order in orders:
        print(sorted(order.keys()))
        for key in keys_in:
            assert key in order
