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
            if resp is not None:
                print("no authentication response")
                return False
            elif (
                isinstance(resp, dict)
                and isinstance(resp['result'], dict)
                and isinstance(resp['result'].get('token'), str)
            ):
                self.token = resp['result']['token']
                return True
            else:
                return False
        except Exception as e:
            print(f"{e} while authenticating")
            return False

    @ pre
    def order_place(self, **kwargs):
        try:
            productType = kwargs.pop('product', 'NRML')
            orderType = kwargs.pop('order_type', 'MARKET')
            orderSide = kwargs.pop('side')
            timeInForce = kwargs.pop('validity', 'DAY')
            disclosedQuantity = kwargs.pop('disclosed_quantity', 0)
            orderQuantity = kwargs.pop('quantity', 0)
            limitPrice = kwargs.pop('trigger_price', 0)
            stopPrice = kwargs.pop('price', 0)
            orderUniqueIdentifier = kwargs.pop('tag', 'no_tag')
            order_args = dict(
                productType=productType,
                orderType=orderType,
                orderSide=orderSide,
                timeInForce=timeInForce,
                disclosedQuantity=disclosedQuantity,
                orderQuantity=orderQuantity,
                limitPrice=limitPrice,
                stopPrice=stopPrice,
                orderUniqueIdentifier=orderUniqueIdentifier,
                clientID=self.user_id,
            )
            order_args.update(kwargs)
            resp = self.broker.place_order(**order_args)
            if (
                resp is not None and isinstance(resp, dict)
                and isinstance(resp['result'], dict)
                and resp['result'].get('AppOrderID', False)
            ):
                return resp['result']['AppOrderID']
            else:
                print(f"resp for args {order_args}")
        except Exception as e:
            print(f"{e} in order_place")

    @ pre
    def order_modify(self, **kwargs):
        try:
            resp = self.broker.modify_order(**kwargs)
        except Exception as e:
            print(f"{e} in order_modify")
        else:
            return resp

    @ pre
    def order_cancel(self, **kwargs):
        try:
            resp = self.broker.cancel_order(**kwargs)
        except Exception as e:
            print(f"{e} in order_cancel")
        else:
            return resp

    @ property
    @ post
    def orders(self) -> list[dict, None]:
        lst = []
        try:
            resp = self.broker.get_order_book(self.user_id)
            lst = resp.get('result')
        except Exception as e:
            print(f"{e} in getting orders")
        else:
            return lst

    @ property
    @ post
    def positions(self) -> list[dict, None]:
        lst = []
        try:
            resp = self.broker.get_position_netwise(self.user_id)
            lst = resp.get('result').get('positionList')
        except Exception as e:
            print(f"{e} in getting net positions")
        else:
            return lst

    @ property
    @ post
    def trades(self) -> list[dict, None]:
        lst = []
        try:
            resp = self.broker.get_trade(self.user_id)
            lst = resp.get('result')
        except Exception as e:
            print(f"{e} in getting trades")
        else:
            return lst

    @ property
    def holdings(self) -> Union[dict, None]:
        lst = []
        try:
            resp = self.broker.get_holding(self.user_id)
            lst = resp.get('result').get("RMSHoldings")
        except Exception as e:
            print(f"{e} in getting holdings")
        else:
            return lst

    @ property
    def margins(self):
        lst = []
        try:
            resp = self.broker.get_balance(self.user_id)
            lst_bal = resp.get('result').get("BalanceList")
            # Extract 'limitObject' values from the list of dictionaries
            lst_lmt = [obj['limitObject']
                       for obj in lst_bal if 'limitObject' in obj]
            # Remove 'AccountID' key from each dictionary
            lst = [{k: v for k, v in d.items() if k != 'AccountID'}
                   for d in lst_lmt]
        except Exception as e:
            print(f"{e} in getting margins")
        else:
            return lst
