from pya3 import *
from omspy.base import Broker, pre, post


class AliceBlue(Broker):
    """
    Automated Trading class
    """

    def __init__(self, user_id, api_key):
        self._user_id = user_id
        self._api_key = api_key
        self.broker = Aliceblue(user_id=user_id, api_key=api_key)
        super(AliceBlue, self).__init__()

    def authenticate(self) -> bool:
        """
        Authenticate the user
        """
        token = self.broker.get_session_id()
        if token and len(token) > 0:
            self.token = token
            return True
        return False

    def get_transaction_type(self, side):
        lst_buy = ["BUY", "Buy", "buy", "B"]
        if side in lst_buy:
            return TransactionType.Buy
        return TransactionType.Sell

    def get_order_type(self, order_type):
        if order_type == "LMT":
            return OrderType.Limit
        elif order_type == "SL":
            return OrderType.StopLossLimit
        elif order_type == "SL-M":
            return OrderType.StopLossMarket

        return OrderType.Market

    def get_product_type(self, product):
        if product == "NRML":
            return ProductType.Normal
        return ProductType.Intraday

    @pre
    def order_place(self, **kwargs):
        symbol = kwargs["symbol"].split(":")
        args = dict(
            transaction_type=self.get_transaction_type(kwargs["side"]),
            instrument=self.broker.get_instrument_by_symbol(
                symbol[0], symbol[1]),
            quantity=kwargs["quantity"],
            order_type=self.get_order_type(kwargs["order_type"]),
            product_type=self.get_product_type(kwargs["product"]),
            price=kwargs.get("price", None),
            trigger_price=kwargs.get("trigger_price", None),
            stop_loss=None,
            square_off=None,
            trailing_sl=None,
            is_amo=False,
            order_tag=kwargs.get("tag", "no_tag")
        )
        return self.broker.place_order(**args)

    def order_modify(self, **kwargs):
        symbol = kwargs["symbol"].split(":")
        args = dict(
            transaction_type=self.get_transaction_type(kwargs["side"]),
            instrument=self.broker.get_instrument_by_symbol(
                symbol[0], symbol[1]),
            order_id=kwargs["order_id"],
            quantity=kwargs["quantity"],
            order_type=self.get_order_type(kwargs["order_type"]),
            product_type=self.get_product_type(kwargs["product"]),
            price=kwargs.get("price", None),
            trigger_price=kwargs.get("trigger_price", None),
        )
        return self.broker.modify_order(**args)

    def order_cancel(self, order_id):
        return self.broker.cancel_order(order_id)

    @property
    @post
    def orders(self):
        orders = self.broker.get_order_history("")
        lst = [
            "symbol",
            "quantity",
            "side",
            "validity",
            "price",
            "trigger_price",
            "average_price",
            "filled_quantity",
            "exchange",
            "exchange_order_id",
            "broker_timestamp",
        ]
        if orders and any(orders):
            """
            filter order dict from orders list of dictionaries
            with lst values as keys
            """
            orders = [{k: order[k] for k in lst if k in order}
                      for order in orders]
        return orders

    @ property
    @ post
    def positions(self):
        return self.broker.get_daywise_positions()

    @ property
    @ post
    def trades(self):
        return self.broker.get_trade_book()
