from NorenRestApiPy.NorenApi import NorenApi
from omspy.base import Broker, pre, post
from typing import List, Dict, Union, Set
import pendulum
import pyotp
import logging


class Profitmart(Broker):
    """
    Automated Trading class
    """

    def __init__(
        self,
        user_id: str,
        password: str,
        pin: str,
        vendor_code: str,
        app_key: str,
        imei: str,
    ):
        self._user_id = user_id
        self._password = password
        self._pin = pin
        self._vendor_code = vendor_code
        self._app_key = app_key
        self._imei = imei
        self._broker = NorenApi(
            host="https://profitmax.profitmart.in/NorenWClientTP",
            websocket='wss://profitmax.profitmart.in/NorenWSTP/',
        )
        super(Profitmart, self).__init__()

    @property
    def attribs_to_copy_modify(self) -> Set:
        return {"symbol", "exchange"}

    def login(self) -> Union[Dict, None]:

        if len(self._pin) > 15:
            twoFA = self._pin if len(
                self._pin) == 4 else pyotp.TOTP(self._pin).now()
        else:
            twoFA = self._pin
        return self._broker.login(
            userid=self._user_id,
            password=self._password,
            twoFA=twoFA,
            vendor_code=self._vendor_code,
            api_secret=self._app_key,
            imei=self._imei,
        )

    def authenticate(self) -> bool:
        """
        Authenticate the user
        """
        resp = self.login()
        if resp is None:
            print("no response")
            return False
        elif (
            isinstance(resp, dict)
            and resp.get('susertoken', False)
        ):
            print(f"Happy Trading {resp['uname']}")
            self._token = resp['susertoken']
            return True
        else:
            return False

    def _convert_symbol(self, symbol: str, exchange: str = "NSE") -> str:
        """
        Convert raw symbol to finvasia
        """
        if exchange == "NSE":
            if symbol.endswith("-EQ") or symbol.endswith("-eq"):
                return symbol
            else:
                return f"{symbol}-EQ"
        else:
            return symbol

    @property
    @post
    def orders(self) -> List[Dict]:
        orderbook = self._broker.get_order_book()
        if orderbook is None:
            return []
        if len(orderbook) == 0:
            return orderbook

        order_list = []
        float_cols = ["avgprc", "prc", "rprc", "trgprc"]
        int_cols = ["fillshares", "qty"]
        for order in orderbook:
            try:
                for int_col in int_cols:
                    order[int_col] = int(order.get(int_col, 0))
                for float_col in float_cols:
                    order[float_col] = float(order.get(float_col, 0))
                ts = order["exch_tm"]
                # Timestamp converted to str to facilitate loading into pandas dataframe
                order["exchange_timestamp"] = str(
                    pendulum.from_format(
                        ts, fmt="DD-MM-YYYY HH:mm:ss", tz="Asia/Kolkata"
                    )
                )
                ts2 = order["norentm"]
                order["broker_timestamp"] = str(
                    pendulum.from_format(
                        ts2, fmt="HH:mm:ss DD-MM-YYYY", tz="Asia/Kolkata"
                    )
                )
            except Exception as e:
                logging.error(e)
            order_list.append(order)
        return order_list

    @property
    @post
    def positions(self) -> List[Dict]:
        positionbook = self._broker.get_positions()
        if positionbook is None:
            return []
        if (
            isinstance(positionbook, list)
            and len(positionbook) == 0
        ):
            return positionbook

        position_list = []
        int_cols = [
            "netqty",
            "daybuyqty",
            "daysellqty",
            "cfbuyqty",
            "cfsellqty",
            "openbuyqty",
            "opensellqty",
        ]
        float_cols = [
            "daybuyamt",
            "daysellamt",
            "lp",
            "rpnl",
            "dayavgprc",
            "daybuyavgprc",
            "daysellavgprc",
            "urmtom",
        ]
        for position in positionbook:
            try:
                for int_col in int_cols:
                    position[int_col] = int(position.get(int_col, 0))
                for float_col in float_cols:
                    position[float_col] = float(position.get(float_col, 0))
            except Exception as e:
                logging.error(e)
            position_list.append(position)
        return position_list

    @property
    @post
    def trades(self) -> List[Dict]:
        tradebook = self._broker.get_trade_book()
        if len(tradebook) == 0:
            return tradebook

        trade_list = []
        int_cols = ["flqty", "qty", "fillshares"]
        float_cols = ["prc", "flprc"]
        for trade in tradebook:
            try:
                for int_col in int_cols:
                    trade[int_col] = int(trade.get(int_col, 0))
                for float_col in float_cols:
                    trade[float_col] = float(trade.get(float_col, 0))
            except Exception as e:
                logging.error(e)
            trade_list.append(trade)
        return trade_list

    def get_order_type(self, order_type: str) -> str:
        """
        Convert a generic order type to this specific
        broker's order type string
        returns MKT if the order_type is not matching
        """
        order_types = dict(
            LIMIT="LMT", MARKET="MKT", SL="SL-LMT", SLM="SL-MKT", SLL="SL-LMT"
        )
        order_types["SL-M"] = "SL-MKT"
        order_types["SL-L"] = "SL-LMT"
        return order_types.get(order_type.upper(), "MKT")

    @pre
    def order_place(self, **kwargs) -> Union[str, None]:
        buy_or_sell = kwargs.pop("side")
        product_type = kwargs.pop("product", "I")
        exchange = kwargs.pop("exchange")
        # kwargs['quantity']
        discloseqty = kwargs.pop("disclosed_quantity", 0)
        price_type = kwargs.pop("order_type")
        if price_type:
            price_type = self.get_order_type(price_type)
        tradingsymbol = kwargs.pop("symbol")
        if tradingsymbol and exchange:
            tradingsymbol = tradingsymbol.upper()
            tradingsymbol = self._convert_symbol(
                tradingsymbol, exchange=exchange)
        price = kwargs.pop("price", None)
        if price and price < 0:
            price = 0.05
        trigger_price = kwargs.pop("trigger_price", None)
        if trigger_price and trigger_price < 0:
            trigger_price = 0.05
        retention = kwargs.pop("validity", "DAY")
        remarks = kwargs.pop("tag", "no_remarks")
        order_args = dict(
            buy_or_sell=buy_or_sell,
            product_type=product_type,
            exchange=exchange,
            tradingsymbol=tradingsymbol,
            discloseqty=discloseqty,
            price_type=price_type,
            price=price,
            trigger_price=trigger_price,
            retention=retention,
            remarks=remarks
        )
        # we have only quantity in kwargs now
        order_args.update(kwargs)
        response = self._broker.place_order(**order_args)
        if isinstance(response, dict) and response.get("norenordno") is not None:
            return response["norenordno"]

    def order_cancel(self, order_id: str) -> Union[Dict, None]:
        """
        Cancel an existing order
        """
        return self._broker.cancel_order(orderno=order_id)

    @pre
    def order_modify(self, **kwargs) -> Union[str, None]:
        """
        Modify an existing order
        """
        symbol = kwargs.pop("tradingsymbol")
        order_id = kwargs.pop("order_id", None)
        order_type = kwargs.pop("order_type", "MKT")
        if "discloseqty" in kwargs:
            kwargs.pop("discloseqty")
        if order_type:
            order_type = self.get_order_type(order_type)
        if symbol:
            symbol = self._convert_symbol(symbol).upper()
        order_args = dict(
            orderno=order_id,
            newprice_type=order_type,
            exchange="NSE",
            tradingsymbol=symbol,
        )
        order_args.update(kwargs)
        return self._broker.modify_order(**order_args)

    def instrument_symbol(self, exch: str, txt: str) -> int:
        res = self._broker.searchscrip(exchange=exch, searchtext=txt)
        return res['values'][0].get('token', 0)

    def historical(self, exch: str, tkn: str, fm: str, to: str):
        return self._broker.get_time_price_series(exch, tkn, fm, to)

    def scriptinfo(self, exch: str, tkn: str):
        return self._broker.get_quotes(exch, tkn)


if __name__ == "__main__":
    from toolkit.fileutils import Fileutils

    m = Fileutils().get_lst_fm_yml("../../../profitmart.yaml")
    print(m)
    pmart = Profitmart(user_id=m['uid'],
                       password=m['pwd'],
                       pin=m['factor2'],
                       vendor_code=m['vc'],
                       app_key=m['app_key'],
                       imei="1234",
                       )
    if pmart.authenticate():
        print("success")
    """
    token = pmart.instrument_symbol("NSE", "SBIN-EQ")
    resp = pmart.scriptinfo("NSE", token)
    print(resp)
    resp = pmart.orders
    print(resp)
    """
