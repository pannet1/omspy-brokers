from alphatrade import AlphaTrade
from omspy.base import Broker, pre, post
import pyotp
from typing import List, Dict
from toolkit.fileutils import Fileutils
from toolkit.utilities import Utilities


class Sasonline(Broker):
    """
    Automated Trading class
    """

    def __init__(self, user_id, passwd, totp):
        self.user_id = user_id
        self.passwd = passwd
        self.totp = totp
        pin = f"{int(pyotp.TOTP(totp).now()):06d}"
        if Fileutils().is_file_not_2day('./access_token.txt'):
            AlphaTrade(
                login_id=user_id, password=passwd, twofa=pin, access_token=None)
            Utilities().slp_for(1)
        access_token = open('access_token.txt', 'r').read().rstrip()
        self.broker = AlphaTrade(
            login_id=user_id, password=passwd, twofa=pin, access_token=access_token)
        super(Sasonline, self).__init__()

    def authenticate(self) -> bool:
        """
        Authenticate the user
        """
        try:
            resp = self.broker.get_profile()
            if (
                resp is not None
                and isinstance(resp, dict)
                and isinstance(resp['data'], dict)
            ):
                print(resp['data'])
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
