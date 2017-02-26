import pyzaif
import unittest
import os
import time

class TestPyzaif(unittest.TestCase):
    def setUp(self):
        self.object = pyzaif.API(api_key=os.environ.get("ZAIF_API_KEY"), api_secret=os.environ.get("ZAIF_API_SECRET"))

    def test_request_api(self):
        self.object.request_api(endpoint="/trades/btc_jpy")

    def test_request_tapi(self):
        self.object.request_tapi(params={"nonce": str(time.time()), "method": "trades", "currency_pair": "btc_jpy"})

    def test_ticker(self):
        self.object.ticker()