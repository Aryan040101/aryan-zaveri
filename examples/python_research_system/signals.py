"""Signal construction for the public research-system showcase."""

from __future__ import annotations

from dataclasses import dataclass

from market_data import SYMBOLS


@dataclass(frozen=True)
class Signal:
    t: int
    symbol: str
    side: int
    score: float
    confidence: float
    reason: str


def score_row(row: dict[str, float]) -> float:
    """Public-safe scoring formula using cross-market context."""

    return (
        0.55 * row["macro_pressure"]
        + 0.25 * row["target_ret_5"]
        - 0.16 * row["target_ret_1"]
        + 0.08 * (row["target_volume_ratio"] - 1.0)
        - 0.10 * row["target_vol_10"]
    )


def build_signal(row: dict[str, float], threshold: float) -> Signal:
    score = score_row(row)
    confidence = min(0.99, max(0.0, abs(score) / max(threshold * 3.0, 1e-9)))
    if score > threshold:
        side = 1
        reason = "macro_context_positive"
    elif score < -threshold:
        side = -1
        reason = "macro_context_negative"
    else:
        side = 0
        reason = "below_threshold"
    return Signal(
        t=int(row["t"]),
        symbol=SYMBOLS["target"],
        side=side,
        score=round(score, 8),
        confidence=round(confidence, 4),
        reason=reason,
    )
