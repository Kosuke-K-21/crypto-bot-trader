import enum
from exchange_client import ExchangeClient
from stream import Stream
from data_manager import DataManager
from model import Model
from status import Status
from trader import Trader
from executor import Executor


if __name__ == "__main__":
    # 取引所を決定
    exchange_client = ExchangeClient(enum.GMO)

    # 各クラスを作成
    stream = Stream(exchange_client)
    data_manager = DataManager()
    model = Model()
    status = Status(exchange_client)
    trader = Trader()
    executor = Executor(exchange_client)

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
