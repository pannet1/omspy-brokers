from omspy.brokers.api_helper import ShoonyaApiPy
from omspy.base import Broker, pre, post
from typing import List, Dict, Union, Set
import pendulum
import pyotp
import logging


class Finvasia(Broker):
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
        broker: str = "",
    ):
        self._user_id = user_id
        self._password = password
        self._pin = pin
        self._vendor_code = vendor_code
        self._app_key = app_key
        self._imei = imei
        if broker == "profitmart":
            self.finvasia = ShoonyaApiPy(
                host="https://profitmax.profitmart.in/NorenWClientTP",
                websocket="wss://profitmax.profitmart.in/NorenWSTP/",
            )
        elif broker == "flattrade":
            self.finvasia = ShoonyaApiPy(
                host="https://piconnect.flattrade.in/PiConnectTP/",
                websocket="wss://piconnect.flattrade.in/PiConnectWSTp/",
            )
        else:
            self.finvasia = ShoonyaApiPy()
        super(Finvasia, self).__init__()

    @property
    def attribs_to_copy_modify(self) -> Set:
        return {"symbol", "exchange"}

    def login(self) -> Union[Dict, None]:
        if len(self._pin) > 15:
            twoFA = self._pin if len(self._pin) == 4 else pyotp.TOTP(self._pin).now()
        else:
            twoFA = self._pin
        return self.finvasia.login(
            userid=self._user_id,
            password=self._password,
            twoFA=twoFA,
            vendor_code=self._vendor_code,
            api_secret=self._app_key,
            imei=self._imei,
        )

    def authenticate(self) -> Union[Dict, None]:
        """
        Authenticate the user
        """
        return self.login()

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
        order_list = []
        orderbook = self.finvasia.get_order_book()
        if orderbook:
            float_cols = ["avgprc", "prc", "rprc", "trgprc"]
            int_cols = ["fillshares", "qty"]
            for order in orderbook:
                for int_col in int_cols:
                    order[int_col] = int(order.get(int_col, 0))
                for float_col in float_cols:
                    order[float_col] = float(order.get(float_col, 0))
                # pendulum current datetime
                now = pendulum.now(tz="Asia/Kolkata").format("DD-MM-YYYY HH:mm:ss")
                ts = order.get("exch_tm", now)
                # Timestamp converted to str to facilitate loading into pandas dataframe
                order["exchange_timestamp"] = str(
                    pendulum.from_format(
                        ts, fmt="DD-MM-YYYY HH:mm:ss", tz="Asia/Kolkata"
                    )
                )
                ts2 = order.get("norentm", now)
                order["broker_timestamp"] = str(
                    pendulum.from_format(
                        ts2, fmt="HH:mm:ss DD-MM-YYYY", tz="Asia/Kolkata"
                    )
                )
                order_list.append(order)
        return order_list

    @property
    @post
    def positions(self) -> List[Dict]:
        positionbook = self.finvasia.get_positions()

        if not positionbook or len(positionbook) == 0:
            return [{}]

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
        tradebook = self.finvasia.get_trade_book()
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
        return order_types.get(order_type.upper(), order_type)

    @pre
    def order_place(self, **kwargs) -> Union[str, None]:
        try:
            buy_or_sell = kwargs.pop("side")
            product_type = kwargs.pop("product", "I")
            exchange = kwargs.pop("exchange")
            discloseqty = kwargs.pop("disclosed_quantity", 0)
            price_type = kwargs.pop("order_type", "MARKET")
            if price_type:
                price_type = self.get_order_type(price_type)
            tradingsymbol = kwargs.pop("symbol")
            if tradingsymbol and exchange:
                tradingsymbol = tradingsymbol.upper()
                tradingsymbol = self._convert_symbol(tradingsymbol, exchange=exchange)
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
                remarks=remarks,
            )
            # we have only quantity in kwargs now
            order_args.update(kwargs)
            response = self.finvasia.place_order(**order_args)
            if isinstance(response, dict) and response.get("norenordno") is not None:
                return response["norenordno"]
        except Exception as err:
            print(err)

    @post
    def order_cancel(self, order_id: str) -> Union[Dict, None]:
        """
        Cancel an existing order
        """
        return self.finvasia.cancel_order(orderno=order_id)

    @pre
    def order_modify(self, **kwargs) -> Union[str, None]:
        """
        Modify an existing order
        """
        symbol = kwargs.pop("tradingsymbol")
        order_id = kwargs.pop("order_id", None)
        order_type = kwargs.pop("order_type", "MKT")
        exchange = kwargs.pop("exchange", "NSE")
        if "discloseqty" in kwargs:
            kwargs.pop("discloseqty")
        if order_type:
            order_type = self.get_order_type(order_type)
        if symbol:
            symbol = self._convert_symbol(symbol, exchange).upper()
        order_args = dict(
            orderno=order_id,
            newprice_type=order_type,
            exchange=exchange,
            tradingsymbol=symbol,
        )
        order_args.update(kwargs)
        return self.finvasia.modify_order(**order_args)

    @property
    def margins(self):
        return self.finvasia.get_limits()

    def instrument_symbol(self, exch: str, txt: str):
        res = self.finvasia.searchscrip(exchange=exch, searchtext=txt)
        if res:
            return res["values"][0].get("token", 0)

    def historical(self, exch: str, tkn: str, fm: str, to: str, tf: int = 1):
        """
        ret = api.get_time_price_series(exchange='NSE', token='22',
        starttime=obj_datetime.timestamp(), interval=5)
        interval: acceptable integer values in minutes are
        “1”, ”3”, “5”, “10”, “15”, “30”, “60”, “120”, “240”
        """
        return self.finvasia.get_time_price_series(exch, tkn, fm, to, tf)

    def scriptinfo(self, exch: str, tkn: str):
        return self.finvasia.get_quotes(exch, tkn)
