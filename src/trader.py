import os
from dataclasses import dataclass
from typing import Literal, Optional
from pathlib import Path


@dataclass
class OrderCondition:
    is_execute: bool
    side: Optional[Literal["BUY", "SELL"]]
    price: Optional[float]
    size: Optional[float]


def trading_algorithm(childorders, positions, board, ticker, executions):
    """Calculate the ordering conditions with your algorithm

    You should do the following:

    1. Calculate limit price, ordrer side and size from board, ticker and executions
    2. Judge whether or not to execute from childorders and positions
    """

    ...

    # Mock algorithm: Buy at best bid - 1000 if there are no existing orders
    price = round(ticker["best_bid"] - 1000.0)
    is_execute = True if not len(childorders) else False

    return OrderCondition(is_execute=is_execute, side="BUY", price=price, size=0.01)
