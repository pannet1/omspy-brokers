from alphatrade import AlphaTrade
from omspy.base import Broker, pre, post
import pyotp
from typing import List, Dict


class Sasonline(Broker):
    """
    Automated Trading class
    """

    def __init__(self, user_id, passwd, totp):
        self.user_id = user_id
        self.passwd = passwd
        self.totp = totp
        pin = totp if len(totp) < 11 else f"{int(pyotp.TOTP(totp).now()):06d}"
        self.broker = AlphaTrade(login_id=user_id, password=passwd, twofa=pin)
        super(Sasonline, self).__init__()

    def authenticate(self) -> str:
        """
        Authenticate the user
        """
        try:
            access_token = open('access_token.txt', 'r').read().rstrip()
            self.access_token = access_token
        except Exception as e:
            print('Exception occurred :: {}'.format(e))
            return False
        else:
            return True

    @ pre
    def order_place(self, **kwargs):
        pass

    def order_modify(self, **kwargs):
        pass

    def order_cancel(self, order_id):
        pass

    @ property
    @ post
    def orders(self) -> List[Dict]:
        return self.alice.get_order_history("")

    @ property
    @ post
    def positions(self):
        pass

    @ property
    @ post
    def trades(self):
        pass
