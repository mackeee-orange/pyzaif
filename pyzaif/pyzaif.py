# -*= coding: utf-8 -*-

import json
import requests
import time
import hmac
import hashlib
import urllib
from datetime import datetime
from urllib.parse import urlencode


class API(object):
    def __init__(self, api_key=None, api_secret=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_url = "https://api.zaif.jp/api/1"
        self.tapi_url = "https://api.zaif.jp/tapi"

    def request_api(self, endpoint, params=None):
        url = self.api_url + endpoint
        body = ""
        auth_header = None

        if params:
            body = "?" + urllib.parse.urlencode(params)

        if self.api_key and self.api_secret:
            access_timestamp = str(time.time())
            api_secret = str.encode(self.api_secret)
            text = str.encode(access_timestamp + endpoint + body)
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
            response = s.get(url, params=params)

        content = json.loads(response.content.decode("utf-8"))
        return content

    def request_tapi(self, func_name, params=None):
        url = self.tapi_url
        headers = None

        if params is None:
            params = {}
        else:
            params.update({"method": func_name, "nonce": int(time.mktime(datetime.now().timetuple()))})

        params.update({"method": func_name, "nonce": int(time.mktime(datetime.now().timetuple()))})
        params = urlencode(params)

        if self.api_key and self.api_secret:
            api_secret = self.api_secret.encode('utf-8')

            access_sign = hmac.new(bytearray(api_secret), digestmod=hashlib.sha512)
            access_sign.update(params.encode('utf-8'))

            headers = {
                "key": self.api_key,
                "sign": access_sign.hexdigest()
            }

        with requests.Session() as s:
            if headers:
                s.headers.update(headers)
            response = s.post(url, data=params, headers=headers)

        content = json.loads(response.text)
        if content['success'] == 0:
            raise Exception(content['error'])
        return content['return']

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
        return self.request_api(endpoint, params=params)

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
        return self.request_api(endpoint, params=params)

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
        return self.request_api(endpoint, params=params)

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
        return self.request_api(endpoint, params=params)

    # TODO:API自体には何のでレート算出アルゴリズムを実装
    def x_rate(self, currency_pair="btc_jpy"):
        """
        いろんな通貨間のレート
        :param params:
        pair: 取引ペア＝＞ ( "btc_jpy" "eth_jpy" "etc_jpy" "dao_jpy" "lsk_jpy" "fct_jpy" "xmr_jpy" "rep_jpy" "xrp_jpy" "zec_jpy" "eth_btc" "etc_btc" "lsk_btc" "fct_btc" "xmr_btc" "rep_btc" "xrp_btc" "zec_btc" )
        :return:
        """
        endpoint = "/api/rate/" + currency_pair
        return self.request_api(endpoint, params={currency_pair: currency_pair})

    ### PRIVATE API ###

    def get_info1(self):
        """
        残高などのアカウント情報を取得する
        :param params:
        :return:
        {
	        "success":1,
	        "return":{
		        "funds":{
			        "jpy":15320,
			        "btc":1.389,
                    "xem":100.2,
			        "mona":2600,
			        "kaori":0.1
		        },
		        "deposit":{
			        "jpy":20440,
			        "btc":1.479,
                    "xem":100.2,
			        "mona":3200,
			        "kaori":0.1
		        },
		        "rights":{
			        "info":1,
			        "trade":1,
			        "withdraw":0,
			        "personal_info":0
		        },
		        "trade_count":18,
		        "open_orders":3,
		        "server_time":1401950833
	        }
        }
        """
        return self.request_tapi(func_name="get_info")

    def get_info2(self):
        return self.request_tapi(func_name="get_info2")

    def get_personal_info(self):
        return self.request_tapi(func_name="get_personal_info")

    def get_trade_history(self, **params):
        """
        ユーザー自身の取引履歴を取得します。
        :param params:
        parameter required description data_type default
        from	No	この順番のレコードから取得	numerical	0
        count	No	取得するレコード数	numerical	1000
        from_id	No	このトランザクションIDのレコードから取得	numerical	0
        end_id	No	このトランザクションIDのレコードまで取得	numerical	infinity
        order	No	ソート順	ASC (昇順)もしくは DESC (降順)	DESC
        since	No	開始タイムスタンプ	UNIX time	0
        end	No	終了タイムスタンプ	UNIX time	infinity
        currency_pair	No	通貨ペア。指定なしで全ての通貨ペア	(例) btc_jpy	全ペア
        is_token	No	true：カウンターパーティトークン以外の情報を取得
        false：カウンターパーティトークンの情報を取得	boolean	false
        :return:
        """
        return self.request_tapi(func_name="get_trade_history", params=params)

    def active_orders(self, **params):
        """
        現在有効な注文一覧を取得します（未約定注文一覧）。
        :param params:
        parameter required description data_type default
        currency_pair	No	取得する通貨ペア。指定なしで全ての通貨ペア	(例) btc_jpy	全てのペア
        is_token	No	true：カウンターパーティトークン以外の情報を取得
        false：カウンターパーティトークンの情報を取得	boolean	false
        is_token_both	No	true：全てのアクティブなオーダー情報を取得
        false：currency_pairやis_tokenに従ったオーダー情報を取得	boolean	false
        :return:
        """
        return self.request_tapi(func_name="active_orders", params=params)

    def trade(self, **params):
        """
        新規注文
        :param params:
        parameter required description data_type default
        currency_pair	Yes	発注する通貨ペア	(例) btc_jpy	-
        action	Yes	注文の種類	bid もしくは ask	-
        price	Yes	指値注文価格	numerical	-
        amount	Yes	数量(例: 0.3)	numerical	-
        limit	No	リミット注文価格	numerical
        :return:
        """
        return self.request_tapi(func_name="trade", params=params)

    def new_order(self, **params):
        """
        新規注文
        :param params:
        parameter required description data_type default
        currency_pair	Yes	発注する通貨ペア	(例) btc_jpy	-
        action	Yes	注文の種類	bid もしくは ask	-
        price	Yes	指値注文価格	numerical	-
        amount	Yes	数量(例: 0.3)	numerical	-
        limit	No	リミット注文価格	numerical
        :return:
        """
        return self.request_tapi(func_name="trade", params=params)

    def cancel_order(self, **params):
        """
        :param params:
        parameter required description data_type default
        order_id	Yes	注文ID（tradeまたはactive_ordersで取得できます）	numerical	-
        is_token	No	true：カウンターパーティトークン以外のオーダーを取り消したい時   boolean	false
                        false：カウンターパーティトークンのオーダーを取り消したい時	    boolean	false
        :return:
        """
        return self.request_tapi(func_name="cancel_order", params=params)

    def withdraw(self, **params):
        """
        引き出し
        :param params:
        parameter required description data_type default
        currency	Yes	引き出す通貨	btc もしくは mona	-
        address	Yes	送信先のアドレス	address string	-
        message	No	送信メッセージ(XEMのみ)	ASCII string	-
        amount	Yes	引き出す金額(例: 0.3)	numerical	-
        opt_fee	No	採掘者への手数料(例: 0.003) (XEM以外)	numerical	-
        :return:
        """
        return self.request_tapi(func_name="withdraw", params=params)

    def deposit_history(self, **params):
        """
        入金履歴
        :param params:
        parameter required description data_type default
        currency	Yes	通貨。jpy / btc / mona 等を指定	TEXT
        from	No	この順番のレコードから取得	numerical	0
        count	No	取得するレコード数	numerical	1000
        from_id	No	この入金IDのレコードから取得	numerical	0
        end_id	No	この入金IDのレコードまで取得	numerical	infinity
        order	No	ソート順	ASC (昇順)もしくは DESC (降順)	DESC
        since	No	開始タイムスタンプ	UNIX time	0
        end	No	終了タイムスタンプ	UNIX time	infinity
        :return:
        """
        return self.request_tapi(func_name="deposit_history", params=params)

    def withdraw_history(self, **params):
        """
        出金履歴
        :param params:
        parameter required description data_type default
        currency	Yes	通貨。jpy / btc / mona 等を指定	TEXT
        from	No	この順番のレコードから取得	numerical	0
        count	No	取得するレコード数	numerical	1000
        from_id	No	この出金IDのレコードから取得	numerical	0
        end_id	No	この出金IDのレコードまで取得	numerical	infinity
        order	No	ソート順	ASC (昇順)もしくは DESC (降順)	DESC
        since	No	開始タイムスタンプ	UNIX time	0
        end	No	終了タイムスタンプ	UNIX time	infinity
        :return:
        """
        return self.request_tapi(func_name="withdraw_history", params=params)

