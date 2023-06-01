from omspy_brokers.XTConnect.Connect import XTSConnect
from omspy_brokers.XTConnect.MarketDataSocketClient import MDSocket_io


# Instruments for subscribing
Instruments = [
    {'exchangeSegment': 1, 'exchangeInstrumentID': 2885},
    {'exchangeSegment': 1, 'exchangeInstrumentID': 26000},
    {'exchangeSegment': 2, 'exchangeInstrumentID': 51601}
]


class Wsocket:

    def __init__(self, API_KEY, API_SECRET):
        self.api_key = API_KEY
        self.api_secret = API_SECRET
        self.ws = XTSConnect(self.api_key, self.api_secret, source="WEBAPI")

    def authenticate(self):
        def on_connect():
            """Connect from the socket."""
            print('Market Data Socket connected successfully!')

            # # Subscribe to instruments
            print('Sending subscription request for Instruments - \n' +
                  str(Instruments))
            response = self.ws.send_subscription(Instruments, 1501)
            print('Sent Subscription request!')
            print("Subscription response: ", response)

# Callback on receiving message

        def on_message(data):
            print('I received a message!')

# Callback for message code 1501 FULL

        def on_message1501_json_full(data):
            print('I received a 1501 Touchline message!' + data)

# Callback for message code 1502 FULL

        def on_message1502_json_full(data):
            print('I received a 1502 Market depth message!' + data)

# Callback for message code 1505 FULL

        def on_message1505_json_full(data):
            print('I received a 1505 Candle data message!' + data)

# Callback for message code 1507 FULL

        def on_message1507_json_full(data):
            print('I received a 1507 MarketStatus data message!' + data)

# Callback for message code 1510 FULL

        def on_message1510_json_full(data):
            print('I received a 1510 Open interest message!' + data)

# Callback for message code 1512 FULL

        def on_message1512_json_full(data):
            print('I received a 1512 Level1,LTP message!' + data)

# Callback for message code 1105 FULL

        def on_message1105_json_full(data):
            print('I received a 1105, Instrument Property Change Event message!' + data)

# Callback for message code 1501 PARTIAL

        def on_message1501_json_partial(data):
            print('I received a 1501, Touchline Event message!' + data)

# Callback for message code 1502 PARTIAL

        def on_message1502_json_partial(data):
            print('I received a 1502 Market depth message!' + data)

# Callback for message code 1505 PARTIAL

        def on_message1505_json_partial(data):
            print('I received a 1505 Candle data message!' + data)

# Callback for message code 1510 PARTIAL

        def on_message1510_json_partial(data):
            print('I received a 1510 Open interest message!' + data)

# Callback for message code 1512 PARTIAL

        def on_message1512_json_partial(data):
            print('I received a 1512, LTP Event message!' + data)

# Callback for message code 1105 PARTIAL

        def on_message1105_json_partial(data):
            print('I received a 1105, Instrument Property Change Event message!' + data)

# Callback for disconnection

        def on_disconnect():
            print('Market Data Socket disconnected!')

# Callback for error

        def on_error(data):
            """Error from the socket."""
            print('Market Data Error', data)

        try:
            response = self.ws.marketdata_login()
            self.token = response['result']['token']
            self.user_id = response['result']['userID']
            print("Login: ", response)
        except Exception as e:
            print(f"while authenticate {e}")
            return False
        else:
            soc = MDSocket_io(self.token, self.user_id)
            soc.on_connect = on_connect
            soc.on_message = on_message
            soc.on_message1502_json_full = on_message1502_json_full
            soc.on_message1505_json_full = on_message1505_json_full
            soc.on_message1507_json_full = on_message1507_json_full
            soc.on_message1510_json_full = on_message1510_json_full
            soc.on_message1501_json_full = on_message1501_json_full
            soc.on_message1512_json_full = on_message1512_json_full
            soc.on_message1105_json_full = on_message1105_json_full
            soc.on_message1502_json_partial = on_message1502_json_partial
            soc.on_message1505_json_partial = on_message1505_json_partial
            soc.on_message1510_json_partial = on_message1510_json_partial
            soc.on_message1501_json_partial = on_message1501_json_partial
            soc.on_message1512_json_partial = on_message1512_json_partial
            soc.on_message1105_json_partial = on_message1105_json_partial
            soc.on_disconnect = on_disconnect
            soc.on_error = on_error
            el = soc.get_emitter()
            el.on('connect', on_connect)
            el.on('1501-json-full', on_message1501_json_full)
            el.on('1502-json-full', on_message1502_json_full)
            el.on('1507-json-full', on_message1507_json_full)
            el.on('1512-json-full', on_message1512_json_full)
            el.on('1105-json-full', on_message1105_json_full)
            self.soc = soc
            self.el = el
            return True
