# -*= coding: utf-8 -*-

import json
import requests
import time
import hmac
import hashlib
import urllib

class API(object):
    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_url = "https://api.zaif.jp/api/1"
        self.tapi_url = "https://api.zaif.jp/tapi"

    def request(self, endpoint, method="GET", params=None):
        url = self.api_url + endpoint
        body = ""
        auth_header = None

        if method == "POST":
            body = json.dumps(params)
        else:
            if params:
                body = "?" + urllib.parse.urlencode(params)

        if self.api_key and self.api_secret:
            access_timestamp = str(time.time())
            api_secret = str.encode(self.api_secret)
            text = str.encode(access_timestamp + method + endpoint + body)
            access_sign = hmac.new(api_secret,
                                   text,
                                   hashlib.sha512).hexdigest()
            auth_header = {
                "ACCESS-KEY": self.api_key,
                "ACCESS-TIMESTAMP": access_timestamp,
                "ACCESS-SIGN": access_sign,
                "Content-Type": "application/json"
            }

        with requests.Session() as s:
            if auth_header:
                s.headers.update(auth_header)

            if method == "GET":
                response = s.get(url, params=params)
            else:  # method == "POST":
                response = s.post(url, data=json.dumps(params))

        content = json.loads(response.content.decode("utf-8"))
        return content

    def request_tapi(self, params=None):
        url = self.tapi_url
        body = ""
        auth_header = None

        body = json.dumps(params)

        if self.api_key and self.api_secret:
            access_timestamp = str(time.time())
            api_secret = str.encode(self.api_secret)
            text = str.encode(access_timestamp + body)
            access_sign = hmac.new(api_secret,
                                   text,
                                   hashlib.sha512).hexdigest()
            auth_header = {
                "ACCESS-KEY": self.api_key,
                "ACCESS-TIMESTAMP": access_timestamp,
                "ACCESS-SIGN": access_sign,
                "Content-Type": "application/json"
            }

        with requests.Session() as s:
            if auth_header:
                s.headers.update(auth_header)

            if method == "GET":
                response = s.get(url, params=params)
            else:  # method == "POST":
                response = s.post(url, data=json.dumps(params))

        content = json.loads(response.content.decode("utf-8"))
        return content

    ### PUBLIC API ###

    def ticker(self, currency_pair="btc_jpy", **params):
        """
        ティッカー
        各種最新情報を簡易に取得することができます。
        :param params:
        None
        :return:
        last 最後の取引の価格
        high 24時間での最高取引価格
        low 24時間での最安取引価格
        vwap 出来高加重平均取引
        volume 24時間での取引量
        bid 現在の買い注文の最高価格
        ask 現在の売り注文の最安価格
        {"last": 136315.0, "high": 139090.0, "low": 127375.0, "vwap": 136163.3273, "volume": 15667.9959, "bid": 136260.0, "ask": 136290.0}
        """
        endpoint = "/ticker/" + currency_pair
        return self.request(endpoint, params=params)

    def trades(self, currency_pair="btc_jpy", **params):
        """
        全取引履歴,
        最新の取引履歴を取得できます。
        :param params:
        offset 指定された数だけスキップ
        :return:
        date ???
        price 取引時の価格
        amount 取引量
        tid ???
        currency_pair 通貨ペア
        trade_type ask or bid
        [{"date": 1487996824, "price": 136275.0, "amount": 0.1656, "tid": 33270317, "currency_pair": "btc_jpy", "trade_type": "ask"}, ...]
        """
        endpoint = "/trades/" + currency_pair
        return self.request(endpoint, params=params)

    def board(self, currency_pair="btc_jpy", **params):
        """
        板情報
        板情報を取得できます。
        :param params:
        None
        :return:
        asks 売り注文の情報
        bids 買い注文の情報
        {
            "asks": [
                        [price, amount],
                        ...
                    ],
            "bids": [
                       [price, amount],
                       ...
                    ]
        }

        """
        endpoint = "/depth/" + currency_pair
        return self.request(endpoint, params=params)

    # TODO:API自体には何のでレート算出アルゴリズムを実装
    def rate(self, **params):
        """
        レートの取得
        取引所の注文を元にレートを算出します。
        :param params:
        order_type 注文のタイプ（"sell" or "buy"）
        pair 取引ペア。現在は "btc_jpy" のみです。
        amount 注文での量。（例）0.1
        price 注文での金額。（例）28000
        :return:
        rate 注文のレート
        price 注文の金額
        amount 注文の量
        """
        endpoint = "/api/exchange/orders/rate"
        return self.request(endpoint, params=params)

    # TODO:API自体には何のでレート算出アルゴリズムを実装
    def x_rate(self, pair="btc_jpy"):
        """
        いろんな通貨間のレート
        :param params:
        pair: 取引ペア＝＞ ( "btc_jpy" "eth_jpy" "etc_jpy" "dao_jpy" "lsk_jpy" "fct_jpy" "xmr_jpy" "rep_jpy" "xrp_jpy" "zec_jpy" "eth_btc" "etc_btc" "lsk_btc" "fct_btc" "xmr_btc" "rep_btc" "xrp_btc" "zec_btc" )
        :return:
        """
        endpoint = "/api/rate/" + pair
        return self.request(endpoint, params={pair: pair})

    ### PRIVATE API ###

    def new_order(self, **params):
        """
        新規注文
        :param params:
        pair 取引ペア。現在は "btc_jpy" のみです。
        order_type 注文方法
            order_type は全部で8つあります。
            "buy" 指値注文 現物取引 買い
            "sell" 指値注文 現物取引 売り
            "market_buy" 成行注文 現物取引 買い
            "market_sell" 成行注文 現物取引 売り
            "leverage_buy" 指値注文 レバレッジ取引新規 買い
            "leverage_sell" 指値注文 レバレッジ取引新規 売り
            "close_long" 指値注文 レバレッジ取引決済 売り
            "close_short" 指値注文 レバレッジ取引決済 買い
        rate 注文のレート。（例）28000
        amount 注文での量。（例）0.1
        market_buy_amount 成行買で利用する日本円の金額。（例）10000
        position_id 決済するポジションのID
        stop_loss_rate 逆指値レート ( 逆指値とは？ )
        :return:
        id 新規注文のID
        rate 注文のレート
        amount 注文の量
        order_type 注文方法
        stop_loss_rate 逆指値レート
        pair 取引ぺア
        created_at 注文の作成日時
        """
        endpoint = ""
        return self.request(endpoint, method="POST", params=params, isTapi=True)

