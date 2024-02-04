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
        if session := self.broker.session:
            return True
        else:
            print(f"{session =}")
            return False

    @ pre
    def order_place(self, **kwargs: List[Dict]):
        """
        Place an order
        """
        pass

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
        return [{}]

    @ property
    @ post
    def trades(self) -> List[Dict]:
        return [{}]

    @ property
    @ post
    def positions(self):
        return [{}]

    @property
    def margins(self):
        return [{}]
