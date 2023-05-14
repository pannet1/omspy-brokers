from omspy.base import Broker, pre, post
from kiteconnect import KiteConnect
from typing import List, Dict
import pyotp
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time


class Zerodha(Broker):
    """
    Automated Trading class
    """

    def __init__(self,
                 userid,
                 password,
                 totp,
                 api_key,
                 tokpath='enctoken.txt',
                 enctoken=None):
        try:
            self.userid = userid
            self.password = password
            self.totp = totp
            self.tokpath = tokpath
            self.enctoken = enctoken
            self.api_key = api_key,
            self.kite = KiteConnect(api_key=self._api_key)
            super(Zerodha, self).__init__()
        except Exception as err:
            print(f'{err} while init')

    def authenticate(self) -> bool:
        """
        Authenticate the user
        """
        try:
            if self.enctoken is None:
                print(self.enctoken)
                self._login()
                self.enctoken = open(self.tokpath, 'r').read().rstrip()
            self.kite.set_headers(self.enctoken, self.userid)
        except Exception as err:
            print(f'{err} while authentiating')
        return True

    def _login(self) -> None:
        try:
            # s = Service(ChromeDriverManager().install())
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            driver = webdriver.Chrome(service=ChromeService(
                ChromeDriverManager().install()), options=options)
            # driver = webdriver.Chrome(service=s, options=options)
            driver.get('https://kite.zerodha.com/')
            driver.implicitly_wait(5)
            time.sleep(5)

            # Find User ID and Password input
            username = driver.find_element(
                By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div/div/form/div[2]/input')
            password = driver.find_element(
                By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div/div/form/div[3]/input')

            # Type User ID and Passwod
            username.send_keys(self.userid)
            password.send_keys(self.password)

            # click on Login
            driver.find_element(
                By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div/div/form/div[4]/button').click()

            time.sleep(5)
            # Find input to enter Pin
            pin = driver.find_element("xpath", "//input[@type='text']")

            # Type the Pin
            otp = pyotp.TOTP(self.totp).now()
            twoFA = f"{int(otp):06d}" if len(otp) <= 5 else otp
            pin.send_keys(twoFA)

            # Click on Continue
            driver.find_element(
                By.XPATH, '/html/body/div[1]/div/div/div[1]/div/div/div/form/div[3]/button').click()

            # Store the Cookies and enctoken
            time.sleep(3)
            cookie = driver.get_cookies()

            # Update Enctoken
            for idx, each_dict in enumerate(cookie):
                if each_dict['name'] == 'public_token':
                    # 'kite' is added to Domain for login on web browser
                    cookie[idx]['domain'] = 'kite.zerodha.com'
                if each_dict['name'] == 'enctoken':
                    with open(self.tokpath, 'w+') as wr:
                        wr.write(each_dict['value'])
                    print("Enctoken Updated")

            driver.quit()
            return True

        except Exception as e:
            print("Error while logging in using Selenium. Error: "+str(e))
            traceback.print_exc()
            return False

    @pre
    def order_place(self, **kwargs: List[Dict]):
        """
        Place an order
        """
        order_args = dict(
            variety="regular", validity="DAY"
        )
        order_args.update(kwargs)
        return self.kite.place_order(**order_args)

    @pre
    def order_modify(self, **kwargs: List[Dict]):
        """
        Modify an existing order
        Note
        ----
        All changes must be passed as keyword arguments
        """
        order_id = kwargs.pop("order_id", None)
        order_args = dict(variety="regular")
        order_args.update(kwargs)
        return self.kite.modify_order(order_id=order_id, **order_args)

    @pre
    def order_cancel(self, order_id: str, variety):
        """
        Cancel an existing order
        """
        order_id = kwargs.pop("order_id", None)
        order_args = dict(variety="regular")
        order_args.update(kwargs)
        return self.kite.cancel_order(order_id=order_id, **order_args)

    @property
    @post
    def orders(self):
        status_map = {
            "OPEN": "PENDING",
            "COMPLETE": "COMPLETE",
            "CANCELLED": "CANCELED",
            "CANCELLED AMO": "CANCELED",
            "REJECTED": "REJECTED",
            "MODIFY_PENDING": "WAITING",
            "OPEN_PENDING": "WAITING",
            "CANCEL_PENDING": "WAITING",
            "AMO_REQ_RECEIVED": "WAITING",
            "TRIGGER_PENDING": "WAITING",
        }
        orderbook = self.kite.orders()
        if orderbook:
            for order in orderbook:
                order["status"] = status_map.get(order["status"])
            return orderbook
        else:
            return [{}]

    @property
    @post
    def trades(self) -> List[Dict]:
        tradebook = self.kite.trades()
        if tradebook:
            return tradebook
        else:
            return [{}]

    @property
    @post
    def positions(self):
        position_book = self.kite.positions().get("day")
        if position_book:
            for position in position_book:
                if position["quantity"] > 0:
                    position["side"] = "BUY"
                else:
                    position["side"] = "SELL"
            return position_book
        return [{}]

    @property
    def profile(self):
        return self.kite.profile()

    @property
    def margins(self):
        return self.kite.margins()

    def ltp(self, exchsym):
        return self.kite.ltp(exchsym)
