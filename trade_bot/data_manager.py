import pandas as pd
import yfinance as yf
from datetime import datetime


class DataManager:
    def __init__(self, ticker, start_date, end_date=None):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date if end_date else datetime.now().strftime("%Y-%m-%d")
        self.data = None

    def fetch_data(self):
        """APIからデータを取得し、内部状態を更新します。"""
        self.data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
        return self.data

    def update_data(self):
        """最新のデータを取得して既存のデータセットに追加します。"""
        new_end_date = datetime.now().strftime("%Y-%m-%d")
        new_data = yf.download(self.ticker, start=self.end_date, end=new_end_date)
        self.data = pd.concat([self.data, new_data])
        self.end_date = new_end_date

    def save_data(self, filepath):
        """データをCSVファイルに保存します。"""
        self.data.to_csv(filepath, index=True)

    def load_data(self, filepath):
        """CSVファイルからデータを読み込みます。"""
        self.data = pd.read_csv(filepath, index_col=0, parse_dates=True)


# 使用例
ticker = "BTC-USD"
start_date = "2020-01-01"

manager = CryptoDataManager(ticker, start_date)
manager.fetch_data()  # データの初期取得
manager.save_data("initial_crypto_data.csv")  # データの保存

# ある時間が経過した後にデータを更新
manager.update_data()
manager.save_data("updated_crypto_data.csv")  # 更新データの保存

if __name__ == "__main__":
    from datetime import datetime
    import time

    import requests
    import pandas as pd

    url = "https://api.bybit.com/v5/market/kline"
    symbol = "BTCUSDT"
    # spot,linear,inverse
    category = "linear"
    # 1,3,5,15,30,60,120,240,360,720,D,M,W
    interval = 15

    timestamp = int(time.time())
    values = []

    while True:
        params = {
            "symbol": symbol,
            "interval": interval,
            "category": category,
            "start": (timestamp - 200 * 60 * interval) * 1000,
            "end": timestamp * 1000,
            "limit": 200,
        }

        response = requests.get(url, params=params)
        response_data = response.json()

        if len(response_data["result"]["list"]) == 0:
            break

        values += response_data["result"]["list"]
        timestamp -= 200 * 60 * interval

    data = pd.DataFrame(values)
    data.to_csv(f"bybit_{symbol}_{category}_{interval}.csv", index=False)

    # カラム名を修正
    data.columns = ["timestamp", "open", "high", "low", "close", "volume", "turnover"]
    # タイムスタンプをdatetime型に変換
    data["datetime"] = (data["timestamp"].astype(int) / 1000).apply(
        datetime.fromtimestamp
    )
    # 昇順に並び替え
    data.sort_values("datetime", inplace=True)
    # "datetime"をインデックスに設定
    data.set_index("datetime", inplace=True)
