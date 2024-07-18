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
