from omspy.base import Broker, pre, post
from dhanhq import dhanhq
from typing import List, Dict


class Dhanhq(Broker):
    """
    Automated Trading class
    """

    def __init__(self, userid, access_token):

        self.userid = userid
        self.broker = dhanhq(client_id=userid, access_token=access_token)
        super(Dhanhq, self).__init__()

    def authenticate(self) -> bool:
        """
        Authenticate the user
        """
        dct_margin = self.broker.get_fund_limits()
        if dct_margin and \
                isinstance(dct_margin, dict) and \
                dct_margin["status"] == "success":
            return True
        return False

    def get_exchange_segment(self, exchange):
        dct = dict(
            NSE=self.broker.NSE,
            BSE=self.broker.BSE,
            CUR=self.broker.CUR,
            MCX=self.broker.MCX,
            FNO=self.broker.FNO,
            NSE_FNO=self.broker.NSE_FNO,
            BSE_FNO=self.broker.BSE_FNO,
            NFO=self.broker.NSE_FNO,
            BFO=self.broker.BSE_FNO
        )
        return dct.get(exchange, self.broker.NSE_FNO)

    def get_order_type(self, order_type):
        dct = dict(
            LMT=self.broker.LIMIT,
            MKT=self.broker.MARKET,
            SLM=self.broker.SLM,
            SL=self.broker.SL
        )
        return dct.get(order_type, self.broker.MARKET)

    def get_product_type(self, product_type):
        dct = dict(
            MIS=self.broker.INTRA,
            NRML=self.broker.DAY,
        )
        return dct.get(product_type, self.broker.MARGIN)

    @ pre
    def order_place(self, **kwargs: List[Dict]):
        """
        Place an order
        """
        symbol = kwargs.pop("symbol")

        args = dict(
            exchange_segment=self.get_exchange_segment(symbol[0]),
            security_id=str(symbol[1]),
            transaction_type=self.broker.BUY if kwargs["side"].upper()[
                0] == "B" else self.broker.SELL,
            quantity=kwargs["quantity"],
            order_type=self.get_order_type(kwargs["order_type"]),
            product_type=self.get_product_type(kwargs["product"]),
            price=kwargs["price"],
            trigger_price=kwargs["trigger_price"]
        )
        self.broker.place_order(**args)

    @ pre
    def order_modify(self, **kwargs: List[Dict]):
        """
        Modify an existing order
        Note
        ----
        All changes must be passed as keyword arguments
        """
        pass

    @ pre
    def order_cancel(self, order_id: str, variety):
        """
        Cancel an existing order
        """
        pass

    @ property
    @ post
    def orders(self):
        return self.broker.get_order_list()

    @ property
    @ post
    def trades(self) -> List[Dict]:
        return [{}]

    @ property
    @ post
    def positions(self):
        return self.broker.get_positions()

    @property
    def margins(self):
        return self.broker.get_fund_limits()
