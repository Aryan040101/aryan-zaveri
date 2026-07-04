"""Feature generation using only information available at decision time."""

from __future__ import annotations

from math import sqrt

from market import GLOBAL, OIL, TARGET, MarketFrame


def simple_return(frames: list[MarketFrame], index: int, symbol: str, lookback: int) -> float:
    if index - lookback < 0:
        raise ValueError("not enough history for requested lookback")
    prev = frames[index - lookback].prices[symbol]
    if prev == 0:
        return 0.0
    return frames[index].prices[symbol] / prev - 1.0


def rolling_volatility(frames: list[MarketFrame], index: int, symbol: str, window: int) -> float:
    if index - window < 0:
        raise ValueError("not enough history for requested window")
    returns = [simple_return(frames, i, symbol, 1) for i in range(index - window + 1, index + 1)]
    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / len(returns)
    return sqrt(variance)


def build_features(frames: list[MarketFrame], index: int) -> dict[str, float]:
    """Build lag-safe features for a decision at ``frames[index]``.

    The replay fills orders on a later frame, so these features may use the
    current frame and prior frames, but never future frames.
    """

    if index < 8:
        raise ValueError("index must be at least 8")

    target_1 = simple_return(frames, index, TARGET, 1)
    target_3 = simple_return(frames, index, TARGET, 3)
    global_3 = simple_return(frames, index, GLOBAL, 3)
    oil_3 = simple_return(frames, index, OIL, 3)
    target_vol_6 = rolling_volatility(frames, index, TARGET, 6)
    global_1 = simple_return(frames, index, GLOBAL, 1)
    oil_1 = simple_return(frames, index, OIL, 1)

    return {
        "target_ret_1": target_1,
        "target_ret_3": target_3,
        "global_ret_1": global_1,
        "global_ret_3": global_3,
        "oil_ret_1": oil_1,
        "oil_ret_3": oil_3,
        "target_vol_6": target_vol_6,
        "context_spread": global_3 - 0.45 * oil_3,
    }

