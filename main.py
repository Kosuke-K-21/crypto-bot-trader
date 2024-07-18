
class Stream():
    def __init__(self, api_key, secret_key):
        self.client = ExchangeClient(api_key, secret_key)

    def get_market_data(self, start_unix):
        # ここでAPIを叩いてデータを取得する
        return data
    

class DataManager():
    def __init__(self):
        self.data = []

    def add(self, data):
        self.data.append(data)

    def tail(self, length: int = 5):
        return self.data[-length:]
    
class Model():
    def translate(self, data):
        # ここでデータを指標に変換する
        return metrics

class Status():
    def __init__(self, exchange_client: ExchangeClient):
        self.client = exchange_client

    def get(self, symbol):
        # ここでステータスを取得する
        return status
    
class Trader():
    """
    Generate actions based on metrics and status
    """
    def cal(self, metrics, status):
        # ここでアクションを計算する
        return actions



if __name__ == '__main__':
while True:
	# 新規データ取得
	data = stream.get_market_data(target_start_unix)

	# データ追加
	data_manager.add(data)

	# データ => 指標への変換
	metrics = model.translate(data_manager.tail())

	# ステータス取得
	status = status.get(symbol)

	# アクション生成
	actions = trader.cal(metrics, status)

	# 執行
	result = executor.request(actions)