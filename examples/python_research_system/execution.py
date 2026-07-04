"""Order-intent and fill simulation for the public Python system."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderIntent:
    t: int
    symbol: str
    action: str
    side: int
    quantity: int
    reference_price: float
    limit_price: float
    reason: str


@dataclass(frozen=True)
class Fill:
    t: int
    symbol: str
    action: str
    side: int
    quantity: int
    reference_price: float
    fill_price: float
    fee: float
    slippage_cost: float


def adaptive_limit(side: int, reference_price: float, max_slippage_bps: float = 4.0) -> float:
    lean = max_slippage_bps / 10_000.0 * 0.35
    return reference_price * (1.0 + lean if side > 0 else 1.0 - lean)


def simulate_fill(intent: OrderIntent, market_price: float, fee_bps: float = 2.0, slippage_bps: float = 1.2) -> Fill:
    execution_side = intent.side if intent.action == "OPEN" else -intent.side
    slip = slippage_bps / 10_000.0
    fill_price = market_price * (1.0 + slip if execution_side > 0 else 1.0 - slip)
    notional = abs(fill_price * intent.quantity)
    return Fill(
        t=intent.t,
        symbol=intent.symbol,
        action=intent.action,
        side=intent.side,
        quantity=intent.quantity,
        reference_price=round(intent.reference_price, 4),
        fill_price=round(fill_price, 4),
        fee=round(notional * fee_bps / 10_000.0, 4),
        slippage_cost=round(abs(fill_price - market_price) * intent.quantity, 4),
    )
