from abc import ABCMeta, abstractmethod


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
    def __init__(self, api_key: str, sec_key: str) -> None:
        self.long_size = 0
        self.short_size = 0
        self.cash = 100000.0
        self.order_id_sequence = 100000
        self.maker_fee = 0.0001
        self.ltp = 0
        self.orders = {}
        self.profit_list = []
        pass

    def create_order(
        self,
        symbol: exchange.Symbol,
        side: exchange.Side,
        order_type: exchange.OrderType,
        size: float,
        price: Optional[float] = None,
        stop_loss: Optional[float] = None,
        close_pos: bool = False,
    ) -> Tuple[Optional[str], Optional[str]]:
        self.order_id_sequence += 1
        self.orders[str(self.order_id_sequence)] = {
            "side": side,
            "order_type": order_type,
            "size": size,
            "price": price,
        }
        return str(self.order_id_sequence), None

    def cancel_order(self, symbol: exchange.Symbol, order_id: str) -> Optional[str]:
        self.orders.pop(order_id, None)
        self.orders = {}
        return None

    def _cancel_order_with_id(
        self, symbol: exchange.Symbol, order_id: str
    ) -> Optional[str]:
        self.orders.pop(order_id, None)
        return None

    def order_list(
        self, symbol: exchange.Symbol
    ) -> Tuple[Optional[List[exchange.Order]], Optional[str]]:
        ret = []
        for key in self.orders.keys():
            obj = self.orders[key]
            ret.append(
                exchange.Order(str(key), obj["price"], obj["size"], obj["side"], 0)
            )
        return ret, None

    def position(
        self, symbol: exchange.Symbol
    ) -> Tuple[Optional[exchange.Position], Optional[str]]:
        return (
            exchange.Position(
                self.long_size, self.short_size, self.long_size - self.short_size
            ),
            None,
        )

    def candles(
        self,
        symbol: exchange.Symbol,
        interval_min: int,
        from_unix: int,
        limit: int = None,
    ) -> Tuple[Optional[List[exchange.OHLCV]], Optional[str]]:
        if (
            from_unix in self.candle_map
            and from_unix + constants.interval_sec in self.candle_map
        ):
            return [
                self.candle_map[from_unix],
                self.candle_map[from_unix + constants.interval_sec],
            ], None
        return None, "no data"

    def balance_of(self, coin: exchange.Coin) -> Tuple[Optional[float], Optional[str]]:
        # 損益情報の蓄積
        pos = self.long_size - self.short_size
        return self.cash + self.ltp * pos, None

    def enque_candles(self, candles: List[exchange.OHLCV]) -> Optional[str]:
        self.candle_map = {}
        for c in candles:
            self.candle_map[c.start_at] = c
        return None

    def apply_candle(self, candle: exchange.OHLCV) -> Optional[str]:
        self.ltp = candle.close
        # 約定確認
        delete_ids = []
        for order_id in self.orders.keys():
            order = self.orders[order_id]
            if order["side"] == exchange.Side.BUY:
                if order["price"] > candle.low:
                    self.long_size += order["size"]
                    self.cash -= order["size"] * order["price"] * (1 - self.maker_fee)
                    delete_ids.append(order_id)
            else:
                if order["price"] < candle.high:
                    self.short_size += order["size"]
                    self.cash += order["size"] * order["price"] * (1 + self.maker_fee)
                    delete_ids.append(order_id)

        base_size = min(self.long_size, self.short_size)
        self.long_size -= base_size
        self.short_size -= base_size

        # 約定したオーダーの削除
        for order_id in delete_ids:
            self._cancel_order_with_id(constants.symbol, order_id)

        # 損益情報の蓄積
        balance, _ = self.balance_of(exchange.Coin.BTC)
        self.profit_list.append(
            exchange.Profit(
                candle.start_at + constants.interval_sec,
                balance,
                ltp=candle.close,
            )
        )
        return None

    def profits(self) -> List[exchange.Profit]:
        return self.profit_list
