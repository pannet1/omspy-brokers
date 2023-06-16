# Replace "file_name" with the actual name of the Python file you want to import
from omspy_brokers.XTConnect.Connect import XTSConnect
from omspy.base import Broker, pre, post
from typing import Union


class Xts(Broker):

    def __init__(
        self,
        API_KEY="YOUR_API_KEY_HERE",
        API_SECRET="YOUR_API_SECRET_HERE",
        userID="YOUR_USER_ID_HERE",
        XTS_API_BASE_URL="https://xts-api.trading",
    ):
        self.api = API_KEY
        self.secret = API_SECRET
        self.user_id = userID
        self.base_url = XTS_API_BASE_URL
        source = "WEBAPI"
        self.broker = XTSConnect(self.api, self.secret, source)
        super(Xts, self).__init__()

    def authenticate(self) -> bool:
        try:
            resp = self.broker.interactive_login()
            self.token = resp.get('result').get('token')
        except Exception as e:
            print(f"{e} while authenticating")
            return False
        else:
            return True

    @pre
    def order_place(self, **kwargs):
        try:
            resp = self.broker.place_order(**kwargs)
        except Exception as e:
            print(f"{e} in order_place")
        else:
            return resp

    @pre
    def order_modify(self, **kwargs):
        try:
            resp = self.broker.modify_order(**kwargs)
        except Exception as e:
            print(f"{e} in order_modify")
        else:
            return resp

    @pre
    def order_cancel(self, **kwargs):
        try:
            resp = self.broker.cancel_order(**kwargs)
        except Exception as e:
            print(f"{e} in order_cancel")
        else:
            return resp

    @property
    @post
    def orders(self) -> list[dict, None]:
        lst = []
        try:
            resp = self.broker.get_order_book(self.user_id)
            lst = resp.get('result')
        except Exception as e:
            print(f"{e} in getting orders")
        else:
            return lst

    @property
    @post
    def positions(self) -> list[dict, None]:
        lst = []
        try:
            resp = self.broker.get_position_netwise(self.user_id)
            lst = resp.get('result').get('positionList')
        except Exception as e:
            print(f"{e} in getting net positions")
        else:
            return lst

    @property
    @post
    def trades(self) -> list[dict, None]:
        lst = []
        try:
            resp = self.broker.get_trade(self.user_id)
            lst = resp.get('result')
        except Exception as e:
            print(f"{e} in getting trades")
        else:
            return lst

    @property
    def holdings(self) -> Union[dict, None]:
        lst = []
        try:
            resp = self.broker.get_holding(self.user_id)
            lst = resp.get('result').get("RMSHoldings")
        except Exception as e:
            print(f"{e} in getting holdings")
        else:
            return lst

    @property
    def margins(self):
        lst = []
        try:
            resp = self.broker.get_balance(self.user_id)
            lst = resp.get('result')
        except Exception as e:
            print(f"{e} in getting margins")
        else:
            return lst
