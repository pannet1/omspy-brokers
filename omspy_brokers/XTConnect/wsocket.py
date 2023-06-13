from omspy_brokers.XTConnect.Connect import XTSConnect
from omspy_brokers.XTConnect.MarketDataSocketClient import MDSocket_io
import json
from time import sleep


class Wsocket:

    def __init__(self, API_KEY, API_SECRET):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        source = "WEBAPI"
        self.xts = XTSConnect(self.api_key, self.api_secret, source)
        response = self.xts.marketdata_login()
        self.token = response['result']['token']
        self.user_id = response['result']['userID']
        print("Login: ", response)
        self.soc = MDSocket_io(self.token, self.user_id)
        self.soc.on_connect = self.on_connect
        self.soc.on_message = self.on_message
        self.soc.on_disconnect = self.on_disconnect
        self.soc.on_message1501_json_full = self.on_message1501_json_full
        self.el = self.soc.get_emitter()
        self.el.on('connect', self.on_connect)
        self.el.on('1501-json-full', self.on_message1501_json_full)
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
        print("===================================")
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
        print(f"from class {self.dct_tline}")


if __name__ == "__main__":
    import threading
    from toolkit.fileutils import Fileutils
    m = Fileutils().get_lst_fm_yml("../../../../arham_marketdata.yaml")
    ws = Wsocket(m['api'], m['secret'])
    # Instruments for subscribing
    Instruments = [
        {'exchangeSegment': 1, 'exchangeInstrumentID': 2885},
        {'exchangeSegment': 1, 'exchangeInstrumentID': 26000},
        {'exchangeSegment': 2, 'exchangeInstrumentID': 51601}
    ]
    resp = ws.xts.send_subscription(Instruments, 1501)
    print(f"resp /n {resp}")

    def strategy():
        while True:
            resp = ws.xts.get_quote(Instruments, 1501, "JSON")
            # print(f"strategy: {ws.dct_tline}")
            print(resp)
            sleep(1)

    """
    # thread the strategy and then connect to escape the while loop
    # thread the connection first and the run strategy
    """
    # threading.Thread(target=strategy).run()
    # ws.soc.connect()

    # threading.Thread(target=ws.soc.connect, daemon=True).run()
    strategy()
