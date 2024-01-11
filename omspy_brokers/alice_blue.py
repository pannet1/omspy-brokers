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
        self.broker = Aliceblue(user_id=user_id, api_key=api_key)
        super(AliceBlue, self).__init__()

    def authenticate(self) -> bool:
        """
        Authenticate the user
        """
        token = self.broker.get_session_id()
        if token and len(token) > 0:
            self.token = token
            return True
        return False

    @pre
    def order_place(self, **kwargs):
        return self.broker.place_order(**kwargs)

    def order_modify(self, **kwargs):
        return self.broker.modify_order(**kwargs)

    def order_cancel(self, order_id):
        return self.broker.cancel_order(order_id)

    @property
    @post
    def orders(self):
        return self.alice.get_order_history("")

    @property
    @post
    def positions(self):
        return self.alice.get_daywise_positions()

    @property
    @post
    def trades(self):
        return self.broker.get_trade_book()
