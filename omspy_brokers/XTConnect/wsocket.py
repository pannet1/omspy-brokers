from omspy_brokers.XTConnect.Connect import XTSConnect
from omspy_brokers.XTConnect.MarketDataSocketClient import MDSocket_io


class Wsocket:

    def __init__(self, API_KEY, API_SECRET):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        source = "WEBAPI"
        self.xts = XTSConnect(self.api_key, self.api_secret, source)

    def authenticate(self):
        try:
            response = self.xts.marketdata_login()
            self.token = response['result']['token']
            self.user_id = response['result']['userID']
            print("Login: ", response)
            self.soc = MDSocket_io(self.token, self.user_id)
        except Exception as e:
            print(f"while authenticate {e}")
            return False
        else:
            return True
