from alphatrade import AlphaTrade
from omspy.base import Broker, pre, post
import pyotp
from toolkit.fileutils import Fileutils
from toolkit.utilities import Utilities


class Sasonline(Broker):
    """
    Automated Trading class
    """
    def __init__(self, user_id, passwd, totp,
        lst_exch=['NSE', 'BSE', 'CDS', 'MCX', 'NFO']
                 ):
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
            login_id=user_id, password=passwd, twofa=pin, access_token=access_token, master_contracts_to_download=lst_exch)
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
        return self.broker.place_order(**kwargs)

    def order_modify(self, **kwargs):
        return self.broker.modify_order(**kwargs)

    def order_cancel(self, **kwargs):
        return self.broker.cancel_order(**kwargs)

    @ property
    @ post
    def orders(self) -> dict:
        try:
            resp = self.broker.get_order_history()
            if resp is None:
                return {}
            elif (
                isinstance(resp, dict)
                and isinstance(resp['data'], dict)
            ):
                return resp['data']
        except Exception as e:
            print(f"exception {str(e)} in orders")
            return {[]}

    @ property
    @ post
    def positions(self) -> dict:
        try:
            resp = self.broker.get_daywise_positions()
            if resp is None:
                return {}
            elif (
                isinstance(resp, dict)
                and isinstance(resp['data'], dict)
            ):
                return resp['data']
        except Exception as e:
            print(f"exception {str(e)} in orders")
            return {}

    @ property
    @ post
    def trades(self) -> dict:
        try:
            resp = self.broker.get_trade_book()
            if resp is None:
                return {}
            elif (
                isinstance(resp, dict)
                and isinstance(resp['data'], dict)
            ):
                return resp['data']
        except Exception as e:
            print(f"exception {str(e)} in orders")
            return {}


if __name__ == "__main__":
    from pprint import pprint
    dct = Fileutils().get_lst_fm_yml("../../../sas.yaml")
    # sas = Sasonline(dct['login_id'], dct['password'], dct['totp'])
    sas = Sasonline(**dct)
    if sas.authenticate():
        print("logging in success")
    resp = sas.positions
    resp = sas.trades
    resp = sas.orders
    pprint(resp)
