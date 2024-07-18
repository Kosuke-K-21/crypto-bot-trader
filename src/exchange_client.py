from typing import Optional, Tuple
from dataclasses import dataclass
from abc import ABCMeta, abstractmethod

@dataclass
class Exchange:
    
    

class ExchangeClient(metaclass=ABCMeta):
    def __init__(self, api_key, secret_key):
        self.api_key = api_key
        self.secret_key = secret_key

    def candles(self, symbol, interval, start_unix):
        # ここでAPIを叩いてデータを取得する
        pass

    def create_order(self, symbol, side, type, quantity, price):
        # ここでAPIを叩いて注文を出す
        pass

    def cancel_order(self, symbol, order_id):
        # ここでAPIを叩いて注文をキャンセルする
        pass

    def balance(self):
        # ここでAPIを叩いて残高を取得する
        pass


class BackTestFiatBase(ExchangeClient):
    def __init__(self, api_key: str, secret_key: str) -> None:
        self.long_size = 0
        self.short_size = 0
        self.cash = 100000.0
        self.order_id_sequence = 100000
        self.maker_fee = 0.0001
        self.ltp = 0
        self.orders = {}
        self.profit_list = []

    def create_order(
            self, 
            symbol: str,
            side: str,
            order_type: str,
            size: float,
            price: Optional[float] = None,
            stop_loss: Optional[float] = None,
            close_pos: Optional[bool] = False
    ) -> Tuple[Optional[str], Optional[str]:
        self.order_id_sequence += 1
        self.orders[str(self.order_id_sequence)] = {
            "side": side,
            "order_type": order_type,
            "size": size,
            "price": price,
        }
        return str(self.order_id_sequence), None
    
    def cancel_order(self, symbol: str, order_id: str) -> Optional[str]:
        self.orders.pop(order_id, None)
        self.orders = {}
        return None
    
    def _cancel_order_with_id(self, order_id: str) -> Optional[str]:
        self.orders.pop(order_id, None)
        return None
    
    def order_list(
        self, symbol: str
        ) -> Tuple[Optional[List[]]]