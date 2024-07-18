class Stream:
    def __init__(self, api_key, secret_key):
        self.client = ExchangeClient(api_key, secret_key)

    def get_market_data(self, start_unix):
        # ここでAPIを叩いてデータを取得する
        return data
