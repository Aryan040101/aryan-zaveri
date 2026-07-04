"""Order intents and deterministic fill accounting for the public demo."""

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
    notional: float
    fee: float
    slippage_cost: float


def simulate_fill(intent: OrderIntent, market_price: float, fee_bps: float = 2.0, slippage_bps: float = 1.5) -> Fill:
    """Fill an intent with side-aware slippage and fees."""

    if intent.quantity <= 0:
        raise ValueError("intent quantity must be positive")

    direction = intent.side
    if intent.action == "CLOSE":
        direction = -intent.side
    slip = slippage_bps / 10_000.0
    fill_price = market_price * (1.0 + slip if direction > 0 else 1.0 - slip)
    notional = abs(fill_price * intent.quantity)
    fee = notional * fee_bps / 10_000.0
    slippage_cost = abs(fill_price - market_price) * intent.quantity
    return Fill(
        t=intent.t,
        symbol=intent.symbol,
        action=intent.action,
        side=intent.side,
        quantity=intent.quantity,
        reference_price=round(intent.reference_price, 4),
        fill_price=round(fill_price, 4),
        notional=round(notional, 4),
        fee=round(fee, 4),
        slippage_cost=round(slippage_cost, 4),
    )

