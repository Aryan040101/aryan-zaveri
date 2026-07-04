"""Lag-safe feature engineering for cross-market research."""

from __future__ import annotations

from math import sqrt

from market_data import MarketSlice, SYMBOLS


def pct_return(slices: list[MarketSlice], index: int, symbol: str, lookback: int) -> float:
    if index - lookback < 0:
        raise ValueError("insufficient history")
    prev = slices[index - lookback].closes[symbol]
    if prev == 0.0:
        return 0.0
    return slices[index].closes[symbol] / prev - 1.0


def rolling_vol(slices: list[MarketSlice], index: int, symbol: str, window: int) -> float:
    if index - window < 0:
        raise ValueError("insufficient history")
    values = [pct_return(slices, i, symbol, 1) for i in range(index - window + 1, index + 1)]
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return sqrt(variance)


def volume_ratio(slices: list[MarketSlice], index: int, symbol: str, window: int = 20) -> float:
    if index - window < 0:
        raise ValueError("insufficient history")
    current = slices[index].volumes[symbol]
    avg = sum(slices[i].volumes[symbol] for i in range(index - window, index)) / window
    return current / avg if avg else 1.0


def build_feature_row(slices: list[MarketSlice], index: int) -> dict[str, float]:
    """Build features available at decision time only."""

    target = SYMBOLS["target"]
    global_symbol = SYMBOLS["global"]
    oil = SYMBOLS["oil"]
    fx = SYMBOLS["fx"]
    vol = SYMBOLS["vol"]

    target_ret_1 = pct_return(slices, index, target, 1)
    target_ret_5 = pct_return(slices, index, target, 5)
    global_ret_3 = pct_return(slices, index, global_symbol, 3)
    oil_ret_3 = pct_return(slices, index, oil, 3)
    fx_ret_3 = pct_return(slices, index, fx, 3)
    vol_ret_3 = pct_return(slices, index, vol, 3)
    target_vol_10 = rolling_vol(slices, index, target, 10)

    return {
        "t": float(slices[index].t),
        "target_ret_1": target_ret_1,
        "target_ret_5": target_ret_5,
        "global_ret_3": global_ret_3,
        "oil_ret_3": oil_ret_3,
        "fx_ret_3": fx_ret_3,
        "vol_ret_3": vol_ret_3,
        "target_vol_10": target_vol_10,
        "target_volume_ratio": volume_ratio(slices, index, target),
        "global_oil_spread": global_ret_3 - 0.45 * oil_ret_3,
        "macro_pressure": global_ret_3 - 0.25 * oil_ret_3 - 0.20 * fx_ret_3 - 0.10 * vol_ret_3,
    }


def build_feature_table(slices: list[MarketSlice], start_index: int = 24) -> list[dict[str, float]]:
    return [build_feature_row(slices, index) for index in range(start_index, len(slices) - 1)]
