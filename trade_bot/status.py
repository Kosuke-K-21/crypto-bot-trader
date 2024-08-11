class Status:
    def __init__(self, exchange_client: ExchangeClient):
        self.client = exchange_client

    def get(self, symbol):
        # ここでステータスを取得する
        return status
