"""Independent pre-trade risk layer for the public showcase."""

from __future__ import annotations

from dataclasses import dataclass

from signals import Signal


@dataclass(frozen=True)
class RiskLimits:
    max_gross_notional: float = 25_000.0
    max_symbol_notional: float = 18_000.0
    max_active_positions: int = 1
    min_confidence: float = 0.35
    max_drawdown: float = 0.08


@dataclass(frozen=True)
class RiskDecision:
    accepted: bool
    reason: str
    quantity: int
    projected_notional: float


def evaluate(signal: Signal, state, price: float, limits: RiskLimits) -> RiskDecision:
    if signal.side == 0:
        return RiskDecision(False, "no_action", 0, 0.0)
    if signal.confidence < limits.min_confidence:
        return RiskDecision(False, "confidence_below_threshold", 0, 0.0)
    if state.current_drawdown <= -limits.max_drawdown:
        return RiskDecision(False, "drawdown_pause", 0, 0.0)
    if len(state.positions) >= limits.max_active_positions:
        return RiskDecision(False, "active_position_limit", 0, 0.0)
    if signal.symbol in state.positions:
        return RiskDecision(False, "duplicate_symbol_position", 0, 0.0)

    deployable = min(limits.max_gross_notional, limits.max_symbol_notional, state.equity * 0.18)
    quantity = int(deployable // price)
    projected = quantity * price
    if quantity <= 0:
        return RiskDecision(False, "quantity_zero", 0, 0.0)
    if projected > limits.max_symbol_notional:
        return RiskDecision(False, "symbol_notional_limit", 0, projected)
    return RiskDecision(True, "approved_by_risk", quantity, projected)
