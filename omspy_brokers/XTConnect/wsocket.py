from omspy_brokers.XTConnect.Connect import XTSConnect
from omspy_brokers.XTConnect.MarketDataSocketClient import MDSocket_io


class Wsocket:

    def __init__(self, API_KEY, API_SECRET):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.ws = XTSConnect(self.api_key, self.api_secret, source="WEBAPI")

    def authenticate(self):
        try:
            response = self.ws.marketdata_login()
            self.token = response['result']['token']
            self.user_id = response['result']['userID']
            print("Login: ", response)
        except Exception as e:
            print(f"while authenticate {e}")
            return False
        else:
            self.soc = MDSocket_io(self.token, self.user_id)
            return True


# Instruments for subscribing
Instruments = [
    {'exchangeSegment': 1, 'exchangeInstrumentID': 2885},
    {'exchangeSegment': 1, 'exchangeInstrumentID': 26000},
    {'exchangeSegment': 2, 'exchangeInstrumentID': 51601}
]
