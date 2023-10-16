from omspy.base import Broker, pre, post
from kiteext.kiteext import KiteExt
from typing import List, Dict
import pyotp
import traceback
import time
import requests
import os


class Bypass(Broker):
    """
    Automated Trading class
    """

    def __init__(self, userid, password, totp, tokpath='enctoken.txt', enctoken=None):

        self.userid = userid
        self.password = password
        self.totp = totp
        self.tokpath = tokpath
        self.enctoken = enctoken
        self.kite = KiteExt(userid=userid)
        super(Bypass, self).__init__()

    def authenticate(self) -> bool:
        """
        Authenticate the user
        """
        if not self.enctoken:
            print(f"{self.enctoken} not found, getting it")
            if self.get_enctoken():
                print(f"got token {self.enctoken}")
                self.enctoken = open(self.tokpath, 'r').read().rstrip()
                print(f"again reading it {self.enctoken}")
        try:
            # self._login()
            print(f"trying to set headers with {self.enctoken}")
            self.kite.set_headers(self.enctoken, self.userid)
        except Exception as err:
            print(f'{err} while authentiating')
            self.remove_token()
            return False
        else:
            return True
        return False

    def get_enctoken(self) -> bool:
        try:
            session = requests.Session()
            data = {'user_id': self.userid, 'password': self.password}
            response = session.post(
                'https://kite.zerodha.com/api/login',
                data=data)
            otp = pyotp.TOTP(self.totp).now()
            twofa = f"{int(otp):06d}"
            response = session.post(
                'https://kite.zerodha.com/api/twofa',
                data={'request_id': response.json()['data']['request_id'],
                      'twofa_value': twofa,
                      'user_id': response.json()['data']['user_id']}
            )
            enctoken = response.cookies.get('enctoken', False)
            if enctoken:
                with open(self.tokpath, 'w+') as wr:
                    wr.write(enctoken)
                self.enctoken = enctoken
            else:
                raise Exception('Enter valid details !!!!')
        except Exception as e:
            print(e)
            return False
        else:
            return True

    @ pre
    def order_place(self, **kwargs: List[Dict]):
        """
        Place an order
        """
        order_args = dict(
            variety="regular", validity="DAY"
        )
        order_args.update(kwargs)
        return self.kite.place_order(**order_args)

    @ pre
    def order_modify(self, **kwargs: List[Dict]):
        """
        Modify an existing order
        Note
        ----
        All changes must be passed as keyword arguments
        """
        order_id = kwargs.pop("order_id", None)
        order_args = dict(variety="regular")
        order_args.update(kwargs)
        return self.kite.modify_order(order_id=order_id, **order_args)

    @ pre
    def order_cancel(self, order_id: str, variety):
        """
        Cancel an existing order
        """
        order_id = kwargs.pop("order_id", None)
        order_args = dict(variety="regular")
        order_args.update(kwargs)
        return self.kite.cancel_order(order_id=order_id, **order_args)

    @ property
    @ post
    def orders(self):
        status_map = {
            "OPEN": "PENDING",
            "COMPLETE": "COMPLETE",
            "CANCELLED": "CANCELED",
            "CANCELLED AMO": "CANCELED",
            "REJECTED": "REJECTED",
            "MODIFY_PENDING": "WAITING",
            "OPEN_PENDING": "WAITING",
            "CANCEL_PENDING": "WAITING",
            "AMO_REQ_RECEIVED": "WAITING",
            "TRIGGER_PENDING": "WAITING",
        }
        orderbook = self.kite.orders()
        if orderbook:
            for order in orderbook:
                order["status"] = status_map.get(order["status"])
            return orderbook
        else:
            return [{}]

    @ property
    @ post
    def trades(self) -> List[Dict]:
        tradebook = self.kite.trades()
        if tradebook:
            return tradebook
        else:
            return [{}]

    @ property
    @ post
    def positions(self):
        position_book = self.kite.positions().get("day")
        if position_book:
            for position in position_book:
                if position["quantity"] > 0:
                    position["side"] = "BUY"
                else:
                    position["side"] = "SELL"
            return position_book
        return [{}]

    @ property
    def profile(self):
        return self.kite.profile()

    @ property
    def margins(self):
        return self.kite.margins()

    @ property
    def remove_token(self):
        if os.path.exists(self.tokpath):
            os.remove(self.tokpath)
        else:
            print(f"not found {self.tokpath}")

    def ltp(self, exchsym):
        return self.kite.ltp(exchsym)

    def history(self, kwargs):
        return self.kite.historical_data(**kwargs)
