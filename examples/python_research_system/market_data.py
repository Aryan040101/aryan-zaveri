"""Synthetic multi-market data generation for the public research showcase."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random


@dataclass(frozen=True)
class Bar:
    t: int
    symbol: str
    close: float
    volume: int


@dataclass(frozen=True)
class MarketSlice:
    t: int
    closes: dict[str, float]
    volumes: dict[str, int]


SYMBOLS = {
    "target": "INDIA_SECTOR",
    "global": "US_SECTOR",
    "oil": "CRUDE_OIL",
    "fx": "USDINR",
    "vol": "VOL_INDEX",
}


def _next(price: float, ret: float) -> float:
    return max(1.0, price * (1.0 + ret))


def generate_market_slices(length: int = 260, seed: int = 17) -> list[MarketSlice]:
    """Generate deterministic market slices with weak cross-market structure."""

    rng = random.Random(seed)
    prices = {
        SYMBOLS["target"]: 100.0,
        SYMBOLS["global"]: 120.0,
        SYMBOLS["oil"]: 80.0,
        SYMBOLS["fx"]: 83.0,
        SYMBOLS["vol"]: 15.0,
    }
    prev_global = 0.0
    prev_oil = 0.0
    prev_fx = 0.0
    out: list[MarketSlice] = []

    for t in range(length):
        cycle = math.sin(t / 13.0)
        global_ret = 0.0003 + cycle * 0.0017 + rng.gauss(0.0, 0.0038)
        oil_ret = 0.0001 - cycle * 0.0008 + rng.gauss(0.0, 0.0032)
        fx_ret = rng.gauss(0.0, 0.0012) + 0.05 * oil_ret
        vol_ret = rng.gauss(0.0, 0.006) - 0.25 * global_ret
        target_ret = (
            0.0002
            + 0.32 * prev_global
            - 0.14 * prev_oil
            - 0.10 * prev_fx
            + math.sin(t / 19.0) * 0.0009
            + rng.gauss(0.0, 0.0042)
        )

        returns = {
            SYMBOLS["target"]: target_ret,
            SYMBOLS["global"]: global_ret,
            SYMBOLS["oil"]: oil_ret,
            SYMBOLS["fx"]: fx_ret,
            SYMBOLS["vol"]: vol_ret,
        }
        for symbol, ret in returns.items():
            prices[symbol] = _next(prices[symbol], ret)

        out.append(
            MarketSlice(
                t=t,
                closes={symbol: round(price, 4) for symbol, price in prices.items()},
                volumes={
                    SYMBOLS["target"]: 100_000 + int(abs(rng.gauss(0, 20_000))),
                    SYMBOLS["global"]: 125_000 + int(abs(rng.gauss(0, 25_000))),
                    SYMBOLS["oil"]: 75_000 + int(abs(rng.gauss(0, 12_000))),
                    SYMBOLS["fx"]: 50_000 + int(abs(rng.gauss(0, 8_000))),
                    SYMBOLS["vol"]: 40_000 + int(abs(rng.gauss(0, 7_000))),
                },
            )
        )
        prev_global = global_ret
        prev_oil = oil_ret
        prev_fx = fx_ret

    return out
