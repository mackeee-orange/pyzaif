import pyzaif
import unittest


class TestPyzaif(unittest.TestCase):
    def setUp(self):
        self.object = pyzaif.API(api_key="***", api_secret="***")

    def test_request_api(self):
        self.object.request_api(endpoint="/trades/btc_jpy")

    def test_request_tapi(self):
        self.object.request_tapi(func_name="get_info")

    def test_ticker(self):
        self.object.ticker()