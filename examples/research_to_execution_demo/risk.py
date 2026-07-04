"""Pre-trade risk gates for the public demo."""

from __future__ import annotations

from dataclasses import dataclass

from signals import Signal


@dataclass(frozen=True)
class RiskLimits:
    max_notional: float = 18_000.0
    max_drawdown: float = 0.06
    risk_fraction: float = 0.16


@dataclass(frozen=True)
class RiskDecision:
    accepted: bool
    reason: str
    projected_notional: float
    quantity: int


def evaluate_signal(signal: Signal, state, price: float, limits: RiskLimits) -> RiskDecision:
    """Convert a signal into a risk decision.

    ``state`` is intentionally duck-typed to avoid circular imports with replay.
    """

    if signal.direction == 0:
        return RiskDecision(False, "no_action", 0.0, 0)
    if state.position is not None:
        return RiskDecision(False, "duplicate_position", 0.0, 0)
    if state.current_drawdown <= -limits.max_drawdown:
        return RiskDecision(False, "drawdown_pause", 0.0, 0)

    deployable = min(limits.max_notional, state.equity * limits.risk_fraction)
    quantity = int(deployable // price)
    projected = quantity * price
    if quantity <= 0:
        return RiskDecision(False, "quantity_zero", projected, 0)
    if projected > limits.max_notional:
        return RiskDecision(False, "notional_limit", projected, 0)
    return RiskDecision(True, "accepted", projected, quantity)

