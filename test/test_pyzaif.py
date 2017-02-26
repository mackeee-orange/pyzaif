from pyzaif import API
import unittest
import os

class TestPyzaif(unittest.TestCase):
    def setUp(self):
        self.object = API(api_key=os.environ.get("ZAIF_API_KEY"), api_secret=os.environ.get("ZAIF_API_SECRET"))

    def test_request_api(self):
        object.request(endpoint="/trades/btc_jpy", isTapi=False)

    def test_request_tapi(self):
        object.request(endpoint="", params={"nonce": ""},isTapi=True)