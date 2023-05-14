from pya3 import Aliceblue
from omspy.base import Broker, pre, post
from typing import List, Dict


class AliceBlue(Broker):
    """
    Automated Trading class
    """

    def __init__(self, user_id, api_key):
        self._user_id = user_id
        self._api_key = api_key
        self.alice = Aliceblue(user_id=user_id, api_key=api_key)
        super(AliceBlue, self).__init__()

    def authenticate(self) -> str:
        """
        Authenticate the user
        """
        return self.alice.get_session_id()

    @pre
    def order_place(self, **kwargs):
        pass

    def order_modify(self, **kwargs):
        pass

    def order_cancel(self, order_id):
        pass

    @property
    @post
    def orders(self) -> List[Dict]:
        return self.alice.get_order_history("")

    @property
    @post
    def positions(self):
        pass

    @property
    @post
    def trades(self):
        pass
