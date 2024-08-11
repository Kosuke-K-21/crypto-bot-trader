from datetime import datetime
import time
from dataclasses import dataclass
import requests
import pandas as pd


@dataclass
class Config:
    url: str = "https://api.bybit.com/v5/market/kline"
    symbol: str = "BTCUSDT"
    category: str = "linear"  # spot,linear,inverse
    interval: int = 30  # 1,3,5,15,30,60,120,240,360,720,D,M,W


if __name__ == "__main__":
    config = Config()

    timestamp = int(time.time())
    values = []

    idx = 0

    while True:
        params = {
            "symbol": config.symbol,
            "interval": config.interval,
            "category": config.category,
            "start": (timestamp - 200 * 60 * config.interval) * 1000,
            "end": timestamp * 1000,
            "limit": 200,
        }

        response = requests.get(url, params=params)
        response_data = response.json()

        if len(response_data["result"]["list"]) == 0:
            break

        values += response_data["result"]["list"]
        timestamp -= 200 * 60 * interval

        idx += 1

        if idx % 3 == 0:
            time.sleep(0.2)

        if len(values) >= 20000:
            break

    data = pd.DataFrame(values)

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

    data.to_csv("data.csv")
