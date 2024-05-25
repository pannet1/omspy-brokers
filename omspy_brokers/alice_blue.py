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
        session = self.broker.get_session_id()
        if isinstance(session, dict):
            if session.get("sessionID", None):
                self.token = session["sessionID"]
                return True
            else:
                print(session.get("emsg", "no error message"))
        return False

    def get_transaction_type(self, side):
        if side[0].upper() == "B":
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
        if product.upper() == "NRML":
            return ProductType.Normal
        return ProductType.Intraday

    def ltp(self, exchange, symbol):
        obj_inst = self.broker.get_instrument_by_symbol(exchange, symbol)
        return float(self.broker.get_scrip_info(obj_inst)["Ltp"])

    def override_buffer(self, price, subtract=False):
        tick = 0.05
        temp = (price * 2) / 100
        price = price - temp if subtract else price + temp
        temp = round(price / tick) * tick
        if temp <= 0:
            temp = tick
        return temp

    def convert_order(self, args, exchange, symbol):
        if "NIFTY" in symbol or (exchange == "NFO" and symbol.endswith("F")):
            return args
        else:
            args["order_type"] = OrderType.Limit
            args["trigger_price"] = 0.0
            print(f"getting ltp for {exchange=} {symbol=}")
            price = self.ltp(exchange, symbol)
            subtract = (
                True if args["transaction_type"] == TransactionType.Sell else False
            )
            args["price"] = self.override_buffer(price, subtract)
            return args

    @pre
    def order_place(self, **kwargs):
        symbol = kwargs["symbol"].split(":")
        args = dict(
            transaction_type=self.get_transaction_type(kwargs["side"]),
            instrument=self.broker.get_instrument_by_symbol(symbol[0], symbol[1]),
            quantity=kwargs["quantity"],
            order_type=self.get_order_type(kwargs["order_type"]),
            product_type=self.get_product_type(kwargs["product"]),
            price=kwargs.get("price", None),
            trigger_price=kwargs.get("trigger_price", None),
            stop_loss=None,
            square_off=None,
            trailing_sl=None,
            is_amo=False,
            order_tag=kwargs.get("tag", "no_tag"),
        )
        if args["order_type"] == OrderType.Market:
            args = self.convert_order(args, symbol[0], symbol[1])
        return self.broker.place_order(**args)

    def order_modify(self, **kwargs):
        symbol = kwargs["symbol"].split(":")
        args = dict(
            transaction_type=self.get_transaction_type(kwargs["side"]),
            instrument=self.broker.get_instrument_by_symbol(symbol[0], symbol[1]),
            order_id=kwargs["order_id"],
            quantity=kwargs["quantity"],
            order_type=self.get_order_type(kwargs["order_type"]),
            product_type=self.get_product_type(kwargs["product"]),
            price=kwargs.get("price", None),
            trigger_price=kwargs.get("trigger_price", None),
        )
        if args["order_type"] == OrderType.Market:
            args = self.convert_order(args, symbol[0], symbol[1])
        return self.broker.modify_order(**args)

    def order_cancel(self, order_id):
        return self.broker.cancel_order(order_id)

    @property
    @post
    def orders(self):
        return self.broker.get_order_history("")

    @property
    @post
    def positions(self):
        return self.broker.get_daywise_positions()

    @property
    @post
    def trades(self):
        return self.broker.get_trade_book()
