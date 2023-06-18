import socketio
from time import sleep
from threading import Thread, RLock
from json import loads, JSONDecodeError
from toolkit.fileutils import Fileutils
from omspy_brokers.XTConnect.Connect import XTSConnect
from omspy_brokers.XTConnect.MarketDataSocketClient import MDSocket_io


class Wsocket:
    SOURCE = "WEBAPI"
    KEYSOFINTEREST = {
        "Open",
        "High",
        "Low",
        "Close",
        "LastTradedPrice",
        "AverageTradedPrice",
        "AskInfo",
        "BidInfo",
    }

    def __init__(self, API_KEY: str, API_SECRET: str) -> None:
        self.message1501_ticks = {}
        self.lock = RLock()
        self.md_api_key = API_KEY
        self.md_api_secret = API_SECRET

        self.xts = XTSConnect(
            self.md_api_key, self.md_api_secret, Wsocket.SOURCE)

        self.md_login_response = self.xts.marketdata_login()

        if (
            self.md_login_response.get("result") is not None
            and isinstance(self.md_login_response, dict)
            and "token" in self.md_login_response["result"]
            and "userID" in self.md_login_response["result"]
            and self.md_login_response["result"].get("token") is not None
            and isinstance(self.md_login_response["result"]["token"], str)
            and self.md_login_response["result"].get("userID") is not None
            and isinstance(self.md_login_response["result"]["userID"], str)
        ):
            self.md_user_id = self.md_login_response["result"]["userID"]
            self.md_token = self.md_login_response["result"]["token"]
            print("UserID:", self.md_user_id, sep=" ", end="\n")
            print("Token:", self.md_token, sep=" ", end="\n")
        else:
            raise Exception(
                "UserID / Token Has Not Been Recieved Or Bad UserID / Token Value"
            )

        self.soc = MDSocket_io(self.md_token, self.md_user_id)

        self.soc.on_connect = self.on_connect
        self.soc.on_message = self.on_message
        self.soc.on_disconnect = self.on_disconnect
        self.soc.on_message1501_json_full = self.on_message1501_json_full
        self.soc.on_message1501_json_partial = self.on_message1501_json_partial

        self.el = self.soc.get_emitter()
        self.el.on("connect", self.on_connect)
        self.el.on("1501-json-full", self.on_message1501_json_full)

        self.soc_thread = Thread(
            target=self.run_soc_forever_with_auto_reconnect,
            name="Wsocket.soc.background.thread",
            daemon=True
        )
        self.soc_thread.start()

    def tprint(self, msg) -> None:
        with self.lock:
            print(msg)

    def run_soc_forever_with_auto_reconnect(self):
        while True:
            try:
                self.soc.connect()
            except socketio.exceptions.ConnectionError as err:
                self.tprint(f"ConnectionError:  {err}")
            except Exception as err:
                self.tprint(f"WebsocketError: {err}")
            else:
                sleep(3)

    def on_connect(self) -> None:
        self.tprint("omspy_broker.XTConnect.Wsocket connected successfully")

    def on_message(self, data) -> None:
        self.tprint(f"message {data} from omspy_broker.Wsocket")

    def on_disconnect(self, data) -> None:
        self.tprint(f"disconnected from omspy_broker.Wsocket due to {data}")

    def on_error(self, data) -> None:
        self.tprint(f"omspy_broker wsocket error {data}")

    def on_message1501_json_partial(self, data) -> None:
        self.tprint(f"I received a 1501, Touchline Event message! {data}")

    def on_message1501_json_full(self, data) -> None:
        try:
            message1501 = loads(data)
        except JSONDecodeError:
            self.tprint(
                f"Encountered An Error While Decoding Json From Data: {data}"
            )
        else:
            self.tprint("=" * 35)
            if (
                message1501.get("ExchangeSegment") is not None
                and message1501.get("ExchangeInstrumentID") is not None
                and message1501.get("Touchline") is not None
                and isinstance(message1501["Touchline"], dict)
            ):
                instrument = '_'.join([
                    str(message1501["ExchangeSegment"]),
                    str(message1501["ExchangeInstrumentID"])
                ])
                message1501_data = {
                    k: v
                    for k, v in message1501["Touchline"].items()
                    if k in Wsocket.KEYSOFINTEREST
                }

                if (
                    isinstance(message1501_data["AskInfo"], dict)
                    and isinstance(message1501_data["BidInfo"], dict)
                    and message1501_data["AskInfo"].get("Price") is not None
                    and message1501_data["BidInfo"].get("Price") is not None
                ):
                    message1501_data["Ask"] = message1501_data["AskInfo"]["Price"]
                    message1501_data["Bid"] = message1501_data["BidInfo"]["Price"]
                    message1501_data.pop("AskInfo", None)
                    message1501_data.pop("BidInfo", None)

                with self.lock:
                    self.message1501_ticks[instrument] = message1501_data
                    print(
                        "from `Wsocket.on_message1501_json_full` method:",
                        f"{self.message1501_ticks}",
                        sep=" ",
                        end="\n"
                    )


if __name__ == "__main__":
    m = Fileutils().get_lst_fm_yml("../../../../arham_marketdata.yaml")
    print(m)
    ws = Wsocket(m["api"], m["secret"])
    # Instruments for subscribing
    Instruments = [
        {"exchangeSegment": 1, "exchangeInstrumentID": 2885},
        {"exchangeSegment": 1, "exchangeInstrumentID": 26000},
        {"exchangeSegment": 2, "exchangeInstrumentID": 51601},
    ]
    resp = ws.xts.send_subscription(Instruments, 1501)
    print(f"resp /n {resp}")

    while True:
        try:
            print(f"strategy: {ws.message1501_ticks}")
        except (KeyboardInterrupt, SystemError, SystemExit):
            break
        else:
            sleep(1)
