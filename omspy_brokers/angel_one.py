from typing import List, Dict
from omspy.base import Broker, pre, post
from SmartApi import SmartConnect
import pyotp


def trunc_name(word: str, leng: str) -> str:
    int_name_len = len(word)
    word = word[leng] if int_name_len > leng else word[:int_name_len]
    return word


class AngelOne(Broker):
    """
    Automated Trading class
    """

    def __init__(self, user_id: str, api_key: str, totp: str, password: str, access_token: str = None, refresh_token=None, feed_token=None):
        self._api_key = api_key
        self._user_id = user_id
        self._totp = totp
        self._password = password
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.feed_token = feed_token
        self.obj = SmartConnect(api_key=api_key, access_token=access_token,
                                refresh_token=refresh_token, feed_token=feed_token)
        otp = pyotp.TOTP(self._totp)
        pin = otp.now()
        pin = f"{int(pin):06d}"
        self.sess = self.obj.generateSession(
            self._user_id, self._password, pin)
        print(f"SESS: {self.sess}")
        if (
            self.sess is not None
            and self.sess.get('data', False)
            and isinstance(self.sess.get('data'), dict)
        ):
            data = self.sess['data']
            jwt = data['jwtToken']
            self.auth_token = jwt.split(' ')[1],
            self.refresh_token = data['refreshToken']
            self.feed_token = data['feedToken']
            p = self.obj.getProfile(self.refresh_token)
            if p is not None and isinstance(p, dict):
                print(f"PROFILE: {p}")
                client_name = p['data']['name'].replace(' ', '')
                int_name_len = len(client_name)
                if int_name_len >= 8:
                    self.client_name = client_name[:8] + \
                        client_name[-3:]
                else:
                    self.client_name = client_name[:int_name_len]
        super(AngelOne, self).__init__()

    def authenticate(self) -> bool:
        """
        Authenticate the user
        """
        if len(self.client_name) > 0:
            return True
        else:
            return False

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
            resp = self.obj.placeOrder(kwargs)
            if (
                resp is not None
                and isinstance(resp, str)
            ):
                return resp
            else:
                print("order no is empty")
                return ""
        except Exception as err:
            print("Order placement failed: {}".format(err))
            return ""

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


if __name__ == '__main__':
    import yaml
    import time

    with open("../../../angel.yaml", 'r') as f:
        ao = AngelOne(**yaml.safe_load(f))
        ao.authenticate()
    print(time.sleep(5))
    new_ao = AngelOne(ao._user_id, ao._api_key, ao._totp, ao._password,
                      ao.access_token, ao.refresh_token, ao.feed_token)
    if new_ao.authenticate():
        print("success")
