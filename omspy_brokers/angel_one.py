from typing import List, Dict
from omspy.base import Broker, pre, post
from smartapi import SmartConnect
import pyotp


def trunc_name(word: str, leng: str) -> str:
    int_name_len = len(word)
    word = word[leng] if int_name_len > leng else word[:int_name_len]
    return word


class AngelOne(Broker):
    """
    Automated Trading class
    """

    def __init__(self, user_id: str, api_key: str, totp: str, password: str):
        self._api_key = api_key
        self._user_id = user_id
        self._totp = totp
        self._password = password
        self._authenticated = False
        try:
            self.obj = SmartConnect(api_key=api_key)
            otp = pyotp.TOTP(self._totp)
            pin = otp.now()
            pin = f"{int(pin):06d}"
            self.sess = self.obj.generateSession(
                self._user_id, self._password, pin)
            print(f"sess {self.sess}")
            super(AngelOne, self).__init__()
        except Exception as err:
            print(f'{err} while init')

    def authenticate(self) -> bool:
        """
        Authenticate the user
        """
        try:
            if not self._authenticated and self.sess:
                if self.sess.get('data', 0) == 0:
                    print("data is not available")
                    return self._authenticated

                data = self.sess['data']
                if data.get('refreshToken', 0) == 0:
                    print("refreshToken is not available")
                    return self._authenticated
                self.refresh_token = self.sess['data']['refreshToken']

                p = self.obj.getProfile(self.refresh_token)
                if p['message'] == 'SUCCESS':
                    print(f"{p}rofile")
                    client_name = p['data']['name'].replace(' ', '')
                    int_name_len = len(client_name)
                    if int_name_len >= 8:
                        self.client_name = client_name[:8] + client_name[-3:]
                    else:
                        self.client_name = client_name[:int_name_len]
                    self._authenticated = True

            return self._authenticated
        except Exception as err:
            print(f'{err} while authenticating')

    @pre
    def order_place(self, **kwargs: List[Dict]):
        try:
            '''
            params = {
                "variety": kwargs["variety"],
                "tradingsymbol": kwargs["tradingsymbol"],
                "symboltoken": kwargs["symboltoken"],
                "transactiontype": kwargs["transactiontype"],
                "exchange": kwargs["exchange"],
                "ordertype": kwargs["ordertype"],
                "producttype": kwargs["producttype"],
                "duration": kwargs["duration"],
                "price": kwargs["price"],
                "triggerprice": kwargs["triggerprice"],
                "quantity": kwargs["quantity"]
                }
            '''
            print(f"trying to place order for {kwargs}")
            return self.obj.placeOrder(kwargs)
        except Exception as err:
            print(f"obj is {self.obj}")
            print(f"kwargs is {kwargs}")
            print("Order placement failed: {}".format(err))

    def order_modify(self, kwargs: List[Dict]):
        try:
            resp = self.obj.modifyOrder(kwargs)
            return resp
        except Exception as err:
            print("Order Modify failed: {}".format(err))

    def order_cancel(self, order_id: str, variety):
        try:
            resp = self.obj.cancelOrder(order_id, variety)
            return resp
        except Exception as err:
            print("Order Cancel failed: {}".format(err))
            return None

    @property
    def profile(self):
        try:
            if self.authenticate():
                resp = self.obj.getProfile(self.refresh_token)
                # r = self.handle_resp(resp, ['clientcode','name'])
                return resp
        except Exception as err:
            return {self._user_id: f'{err}'}

    @property
    @post
    def orders(self) -> dict[str, str]:
        try:
            if self.authenticate():
                resp = self.obj.orderBook()
                return resp
        except Exception as err:
            return {self._user_id: f'{err}'}

    @property
    @post
    def trades(self):
        try:
            if self.authenticate():
                resp = self.obj.tradeBook()
                return resp
        except Exception as err:
            return {self._user_id: f'{err}'}

    @property
    @post
    def positions(self):
        try:
            if self.authenticate():
                resp = self.obj.position()
                return resp
        except Exception as err:
            return {self._user_id: f'{err}'}

    @property
    def margins(self):
        try:
            if self.authenticate():
                resp = self.obj.rmsLimit()
                return resp
        except Exception as err:
            return {self._user_id: f'{err}'}
