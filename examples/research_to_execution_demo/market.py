"""Synthetic multi-asset market data for the public demo."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random


TARGET = "INDIA_EQ"
GLOBAL = "GLOBAL_SECTOR"
OIL = "CRUDE_OIL"


@dataclass(frozen=True)
class MarketFrame:
    """One synthetic time slice across all assets."""

    t: int
    prices: dict[str, float]
    volumes: dict[str, int]


def _next_price(price: float, drift: float, shock: float) -> float:
    return max(1.0, price * (1.0 + drift + shock))


def generate_market(length: int = 180, seed: int = 7) -> list[MarketFrame]:
    """Generate deterministic synthetic market frames.

    The target asset has a weak relationship to lagged global context and oil.
    This relationship exists only to make the demo produce stable behavior.
    """

    rng = random.Random(seed)
    target = 100.0
    global_sector = 120.0
    oil = 80.0
    frames: list[MarketFrame] = []
    prev_global_ret = 0.0
    prev_oil_ret = 0.0

    for t in range(length):
        cycle = math.sin(t / 11.0) * 0.0018
        global_ret = 0.0003 + cycle + rng.gauss(0.0, 0.004)
        oil_ret = 0.0001 - cycle * 0.35 + rng.gauss(0.0, 0.003)
        target_ret = (
            0.0002
            + 0.34 * prev_global_ret
            - 0.18 * prev_oil_ret
            + math.sin(t / 17.0) * 0.001
            + rng.gauss(0.0, 0.0045)
        )

        global_sector = _next_price(global_sector, 0.0, global_ret)
        oil = _next_price(oil, 0.0, oil_ret)
        target = _next_price(target, 0.0, target_ret)

        frames.append(
            MarketFrame(
                t=t,
                prices={
                    TARGET: round(target, 4),
                    GLOBAL: round(global_sector, 4),
                    OIL: round(oil, 4),
                },
                volumes={
                    TARGET: 90_000 + int(abs(rng.gauss(0, 15_000))),
                    GLOBAL: 110_000 + int(abs(rng.gauss(0, 20_000))),
                    OIL: 70_000 + int(abs(rng.gauss(0, 10_000))),
                },
            )
        )
        prev_global_ret = global_ret
        prev_oil_ret = oil_ret

    return frames

