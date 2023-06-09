from omspy_brokers.XTConnect.Connect import XTSConnect
from omspy_brokers.XTConnect.MarketDataSocketClient import MDSocket_io
import json


class Wsocket:

    def __init__(self, API_KEY, API_SECRET):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        source = "WEBAPI"
        self.xts = XTSConnect(self.api_key, self.api_secret, source)
        response = self.xts.marketdata_login()
        print("Login: ", response)
        self.token = response['result']['token']
        self.user_id = response['result']['userID']
        self.soc = MDSocket_io(self.token, self.user_id)
        self.soc.on_connect = self.on_connect
        self.soc.on_message = self.on_message
        self.soc.on_disconnect = self.on_disconnect
        self.soc.on_message1501_json_full = self.on_message1501_json_full
        self.el = self.soc.get_emitter()
        self.el.on('connect', self.on_connect)
        self.dct_tline = {}

    def on_connect(self):
        print("omspy_broker.XTConnect.Wsocket connected successfully")

    def on_message(self, data):
        print(f"message {data} from omspy_broker.Wsocket")

    def on_disconnect(self, data):
        print(f"disconnected from omspy_broker.Wsocket due to {data}")

    def on_error(self, data):
        print(f"omspy_broker wsocket error {data}")

    def on_message1501_json_full(self, data):
        dct = json.loads(data)
        id = str(dct.get("ExchangeSegment")) + "_" + \
            str(dct.get("ExchangeInstrumentID"))
        body = dct.get("Touchline")
        keys_to_extract = [
            'Open',
            'High',
            'Low',
            'Close',
            'LastTradedPrice',
            'AverageTradedPrice',
            'AskInfo',
            'BidInfo'
        ]
        dct = {k: v for k, v in body.items() if k in keys_to_extract}
        dct['Ask'] = dct['AskInfo'].get('Price')
        dct['Bid'] = dct['BidInfo'].get('Price')
        dct.pop('AskInfo')
        dct.pop('BidInfo')
        self.dct_tline[id] = dct
        print(self.dct_tline)
