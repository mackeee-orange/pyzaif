import pyzaif
import unittest
import os

class TestPyzaif(unittest.TestCase):
    def setUp(self):
        self.object = pyzaif.API(api_key=os.environ["ZAIF_API_KEY"], api_secret=os.environ["ZAIF_API_SECRET"])

    def test_request_api(self):
        self.object.request_api(endpoint="/trades/btc_jpy")

    def test_request_tapi(self):
        self.object.request_tapi(func_name="get_info")

    def test_ticker(self):
        self.object.ticker()