"""Toy signal model for the public demo."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Signal:
    t: int
    symbol: str
    score: float
    direction: int
    reason: str


def score_signal(t: int, symbol: str, features: dict[str, float], threshold: float = 0.0028) -> Signal:
    """Score a synthetic signal.

    This is deliberately simple, public-safe logic. It demonstrates how a
    score becomes an action; it is not a real trading strategy.
    """

    score = (
        0.62 * features["context_spread"]
        + 0.25 * features["target_ret_3"]
        - 0.20 * features["target_ret_1"]
        - 0.08 * features["target_vol_6"]
    )
    if score > threshold:
        direction = 1
        reason = "context_positive"
    elif score < -threshold:
        direction = -1
        reason = "context_negative"
    else:
        direction = 0
        reason = "below_threshold"
    return Signal(t=t, symbol=symbol, score=round(score, 8), direction=direction, reason=reason)

