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
                                   hashlib.sha256).hexdigest()
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

    def ticker(self, **params):
        """
        ティッカー
        各種最新情報を簡易に取得することができます。
        :param params:
        None
        :return:
        last 最後の取引の価格
        bid 現在の買い注文の最高価格
        ask 現在の売り注文の最安価格
        high 24時間での最高取引価格
        low 24時間での最安取引価格
        volume 24時間での取引量
        timestamp 現在の時刻
        """
        endpoint = "/ticker"
        return self.request(endpoint, params=params)

    def trades(self, **params):
        """
        全取引履歴,
        最新の取引履歴を取得できます。
        :param params:
        offset 指定された数だけスキップ
        :return:
        """
        endpoint = "/trades"
        return self.request(endpoint, params=params)

    def board(self, **params):
        """
        板情報
        板情報を取得できます。
        :param params:
        None
        :return:
        asks 売り注文の情報
        bids 買い注文の情報
        """
        endpoint = "/depth"
        return self.request(endpoint, params=params)

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
        endpoint = "/api/exchange/orders"
        return self.request(endpoint, method="POST", params=params)

    def outstanding_orders(self, **params):
        """
        未決済の注文一覧
        :param params:
        None
        :return:
        id 注文のID（新規注文でのIDと同一です）
        rate 注文のレート（ null の場合は成り行き注文です）
        pending_amount 注文の未決済の量
        pending_market_buy_amount 注文の未決済の量（現物成行買いの場合のみ）
        order_type 注文のタイプ（"sell" or "buy"）
        stop_loss_rate 逆指値レート
        pair 取引ペア
        created_at 注文の作成日時
        """
        endpoint = "/api/exchange/orders/opens"
        return self.request(endpoint, params=params)

    def cancel_order(self, **params):
        """
        新規注文または未決済の注文一覧のIDを指定してキャンセル
        :param params:
        id  新規注文または未決済の注文一覧のID
        :return:
        id キャンセルした注文のID
        """
        endpoint = "/api/exchange/orders/" + params["id"]
        return self.request(endpoint, method="DELETE", params=params)

    def transactions(self, **params):
        """
        自分の取引履歴
        :param params:
        :return:
        id ID
        order_id 注文のID
        created_at 取引が行われた時間
        funds 各残高の増減分
        pair 取引ペア
        rate 約定価格
        fee_currency 手数料の通貨
        fee 発生した手数料
        liquidity "T" ( Taker ) or "M" ( Maker )
        side "sell" or "buy"
        """
        endpoint = "/api/exchange/orders/transactions"
        return self.request(endpoint, params=params)

    def transactions_pagenations(self, **params):
        """
        自分の最近の取引履歴
        :param params:
        limit 1ページあたりの取得件数を指定できます。
        order "desc", "asc" を指定できます。
        starting_after IDを指定すると絞り込みの開始位置を設定できます。
        ending_before IDを指定すると絞り込みの終了位置を設定できます。
        :return:
        id ID
        order_id 注文のID
        created_at 取引が行われた時間
        funds 各残高の増減分
        pair 取引ペア
        rate 約定価格
        fee_currency 手数料の通貨
        fee 発生した手数料
        liquidity "T" ( Taker ) or "M" ( Maker )
        side "sell" or "buy"
        """
        endpoint = "/api/exchange/orders/transactions_pagination"
        return self.request(endpoint, params=params)

    def positions(self, **params):
        """
        レバレッジ取引のポジション一覧を表示します。レバレッジ取引の注文は 新規注文 から行えます。
        :param params:
        status "open", "closed" を指定できます。
        :return:
        id ID
        pair 取引ペア
        status ポジションの状態 ( "open", "closed" )
        created_at ポジションの作成日時
        closed_at ポジションの決済完了日時
        open_rate ポジションの平均取得価格
        closed_rate ポジションの平均決済価格
        amount 現在のポジションの数量（BTC）
        all_amount ポジションの数量（BTC）
        side ポジションの種類 ( "buy", "sell" )
        pl 利益
        new_order 新規注文についての情報
        close_orders 決済注文についての情報
        """
        endpoint = "/api/exchange/leverage/positions"
        return self.request(endpoint, params=params)

    def balance(self, **params):
        """
        アカウントの残高を確認できます。
        jpy, btc には未決済の注文に利用している jpy_reserved, btc_reserved は含まれていません。
        :param params:
        :return:
        jpy 日本円の残高
        btc ビットコインの残高
        jpy_reserved 未決済の買い注文に利用している日本円の合計
        btc_reserved 未決済の売り注文に利用しているビットコインの合計
        jpy_lend_in_use 貸出申請をしている日本円の合計（現在は日本円貸出の機能を提供していません）
        btc_lend_in_use 貸出申請をしているビットコインの合計（現在はビットコイン貸出の機能を提供していません）
        jpy_lent 貸出をしている日本円の合計（現在は日本円貸出の機能を提供していません）
        btc_lent 貸出をしているビットコインの合計（現在はビットコイン貸出の機能を提供していません）
        jpy_debt 借りている日本円の合計
        btc_debt 借りているビットコインの合計
        """
        endpoint = "/api/accounts/balance"
        return self.request(endpoint, params=params)

    def leverage_balance(self, **params):
        """
        レバレッジアカウントの残高
        :param params:
        :return:
        margin[jpy] 証拠金
        margin_available[jpy] 利用可能な証拠金
        margin_level 証拠金維持率
        """
        endpoint = "/api/accounts/leverage_balance"
        return self.request(endpoint, params=params)

    def send_btc(self, **params):
        """
        ビットコインの送金
        :param params:
        address 送り先のビットコインアドレス
        amount 送りたいビットコインの量
        :return:
        id 送金のIDです
        address 送った先のbitcoinアドレス
        amount 送ったbitcoinの量
        fee 手数料
        """
        endpoint = "/api/send_money"
        return self.request(endpoint, method="POST", params=params)

    def send_btc_log(self, **params):
        """
        送金履歴
        :param params:
        currency 通貨（現在は BTC のみ対応）
        :return:
        id 送金のIDです
        amount 送ったbitcoinの量
        fee 手数料
        currency 通貨
        address 送った先のbitcoinアドレス
        created_at 送金処理の作成日時
        """
        endpoint = "/api/send_money"
        return self.request(endpoint, params=params)

    def receive(self, **params):
        """
        ビットコインの受け取り履歴
        :param params:
        :return:
        id 受け取りのID
        amount 受け取ったビットコインの量
        currency 通貨
        address 受け取り元のビットコインアドレス
        status ステータス
        confirmed_at 受け取りの承認日時
        created_at 受け取り処理の作成日時
        """
        endpoint = "/api/deposit_money"
        return self.request(endpoint, params=params)

    def fast_deposit(self, **params):
        """
        ビットコインの高速入金
        :param params:
        id ビットコイン受取履歴 のID
        :return:
        """
        endpoint = "/api/deposit_money/" + params["id"] + "/fast"
        return self.request(endpoint, method="POST", params=params)

    def account(self, **params):
        """
        アカウント情報
        :param params:
        :return:
        id アカウントのID。日本円入金の際に指定するIDと一致します。
        email 登録されたメールアドレス
        identity_status 本人確認書類の提出状況を表示します。
        bitcoin_address あなたのデポジット用ビットコインのアドレス
        lending_leverage あなたのレバレッジを表示します。
        taker_fee Takerとして注文を行った場合の手数料を表示します。
        maker_fee Makerとして注文を行った場合の手数料を表示します。
        """
        endpoint = "/api/accounts"
        return self.request(endpoint, params=params)

    def bank_accounts(self, **params):
        """
        口座情報
        :param params:
        :return:
        id ID
        bank_name 銀行名
        branch_name 支店名
        bank_account_type 銀行口座の種類（futsu : 普通口座, toza : 当座預金口座）
        number 口座番号
        name 口座名義
        """
        endpoint = "/api/bank_accounts"
        return self.request(endpoint, params=params)

    def register_bank_account(self, **params):
        """
        銀行口座を登録する
        :param params:
        bank_name 銀行名
        branch_name 支店名
        bank_account_type 銀行口座の種類（futsu : 普通口座, toza : 当座預金口座）
        number 口座番号（例）"0123456"
        name 口座名義
        :return:
        id ID
        bank_name 銀行名
        branch_name 支店名
        bank_account_type 銀行口座の種類（futsu : 普通口座, toza : 当座預金口座）
        number 口座番号（例）"0123456"
        name 口座名義
        """
        endpoint = "/api/bank_accounts"
        return self.request(endpoint, method="POST", params=params)

    def delete_bank_account(self, **params):
        """
        銀行口座を削除
        :param params:
        id
        :return:
        """
        endpoint = "/api/bank_accounts/" + params["id"]
        return self.request(endpoint, method="DELETE", params=params)

    def get_withdraws(self, **params):
        """
        出勤履歴
        :param params:
        :return:
        id ID
        status 出金の状態 ( pending 未処理, processing 手続き中, finished 完了, canceled キャンセル済み)
        amount 金額
        currency 通貨
        created_at 作成日時
        bank_account_id 銀行口座のID
        fee 振込手数料
        is_fast 高速出金のオプション
        """
        endpoint = "/api/withdraws"
        return self.request(endpoint, params=params)

    def withdraw(self, **params):
        """
        出勤申請
        :param params:
        bank_account_id 銀行口座のID
        amount 金額
        currency 通貨 ( 現在は "JPY" のみ対応)
        is_fast 高速出金のオプション（デフォルトは false ）
        :return:
        id ID
        status 出金の状態 ( pending 未処理, processing 手続き中, finished 完了, canceled キャンセル済み)
        amount 金額
        currency 通貨 ( 現在は "JPY" のみ対応)
        created_at 作成日時
        bank_account_id 銀行口座のID
        fee 振込手数料
        is_fast 高速出金のオプション（デフォルトは false ）
        """
        endpoint = "/api/withdraws"
        return self.request(endpoint, method="POST", params=params)

    def cancel_withdraw(self, **params):
        """
        出勤申請のキャンセル
        :param params:
        id
        :return:
        """
        endpoint = "/api/withdraws/" + params["id"]
        return self.request(endpoint, method="DELETE", params=params)

    def borrow(self, **params):
        """
        借り入れ申請
        :param params:
        amount 借りたい量
        currency 通貨（BTC, JPY, ETH）
        :return:
        id ID
        rate 日当たりのレート（BTCは0.05%, JPYは0.04%, ETHは0.05%）
        amount 注文の量
        currency 通貨
        created_at 注文の作成日時
        """
        endpoint = "/api/lending/borrows"
        return self.request(endpoint, method="POST", params=params)

    def get_borrows(self, **params):
        """
        借り入れ中一覧
        :param params:
        :return:
        """
        endpoint = "/api/lending/borrows/matches"
        return self.request(endpoint, params=params)

    def repay(self, **params):
        """
        返済する
        :param params:
         id
        :return:
        """
        endpoint = "/api/lending/borrows/" + params["id"] + "/repay"
        return self.request(endpoint, method="POST", params=params)

    def transfer_to_leverage(self, **params):
        """
        現物取引アカウントからレバレッジアカウントへ振替します。
        :param params:
        currency 通貨（現在は JPY のみ対応）
        amount 移動する数量
        :return:
        """
        endpoint = "/api/exchange/transfers/to_leverage"
        return self.request(endpoint, method="POST", params=params)

    def transfer_from_leverage(self, **params):
        """
        レバレッジアカウントから現物取引アカウントへ振替します。
        :param params:
        currency 通貨（現在は JPY のみ対応）
        amount 移動する数量
        :return:
        """
        endpoint = "/api/exchange/transfers/from_leverage"
        return self.request(endpoint, method="POST", params=params)
