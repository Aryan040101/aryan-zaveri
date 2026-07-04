"""Replay loop tying synthetic research, risk and execution together."""

from __future__ import annotations

from dataclasses import dataclass

from execution import OrderIntent, simulate_fill
from features import build_features
from market import TARGET, MarketFrame
from metrics import summarize
from risk import RiskLimits, evaluate_signal
from signals import score_signal


@dataclass
class Position:
    symbol: str
    side: int
    quantity: int
    entry_price: float
    entry_fee: float
    entry_slippage: float
    entry_t: int


@dataclass
class ReplayState:
    starting_equity: float = 100_000.0
    realized_pnl: float = 0.0
    equity: float = 100_000.0
    peak_equity: float = 100_000.0
    current_drawdown: float = 0.0
    position: Position | None = None

    def mark(self, price: float) -> float:
        unrealized = 0.0
        if self.position is not None:
            unrealized = self.position.side * (price - self.position.entry_price) * self.position.quantity
        self.equity = self.starting_equity + self.realized_pnl + unrealized
        self.peak_equity = max(self.peak_equity, self.equity)
        self.current_drawdown = self.equity / self.peak_equity - 1.0
        return self.equity


def _should_close(position: Position, signal_direction: int, t: int, max_hold: int) -> bool:
    if signal_direction and signal_direction != position.side:
        return True
    return t - position.entry_t >= max_hold


def run_replay(frames: list[MarketFrame], limits: RiskLimits | None = None, max_hold: int = 9) -> dict:
    """Run the deterministic public replay."""

    limits = limits or RiskLimits()
    state = ReplayState()
    trades: list[dict] = []
    equity_curve: list[float] = [state.starting_equity]
    accepted = 0
    rejected = 0

    for index in range(8, len(frames) - 1):
        decision_frame = frames[index]
        fill_frame = frames[index + 1]
        decision_price = decision_frame.prices[TARGET]
        fill_price = fill_frame.prices[TARGET]
        state.mark(decision_price)
        equity_curve.append(state.equity)

        features = build_features(frames, index)
        signal = score_signal(decision_frame.t, TARGET, features)

        if state.position is not None and _should_close(state.position, signal.direction, decision_frame.t, max_hold):
            position = state.position
            intent = OrderIntent(
                t=fill_frame.t,
                symbol=TARGET,
                action="CLOSE",
                side=position.side,
                quantity=position.quantity,
                reference_price=decision_price,
                reason="opposite_signal_or_time_exit",
            )
            fill = simulate_fill(intent, fill_price)
            gross = position.side * (fill.fill_price - position.entry_price) * position.quantity
            fees = position.entry_fee + fill.fee
            slippage = position.entry_slippage + fill.slippage_cost
            net = gross - fees
            state.realized_pnl += net
            trades.append(
                {
                    "entry_t": position.entry_t,
                    "exit_t": fill.t,
                    "side": position.side,
                    "quantity": position.quantity,
                    "gross_pnl": round(gross, 4),
                    "fees": round(fees, 4),
                    "slippage_cost": round(slippage, 4),
                    "net_pnl": round(net, 4),
                }
            )
            state.position = None
            state.mark(fill_price)
            equity_curve.append(state.equity)

        decision = evaluate_signal(signal, state, decision_price, limits)
        if decision.accepted:
            intent = OrderIntent(
                t=fill_frame.t,
                symbol=TARGET,
                action="OPEN",
                side=signal.direction,
                quantity=decision.quantity,
                reference_price=decision_price,
                reason=signal.reason,
            )
            fill = simulate_fill(intent, fill_price)
            state.realized_pnl -= fill.fee
            state.position = Position(
                symbol=TARGET,
                side=signal.direction,
                quantity=decision.quantity,
                entry_price=fill.fill_price,
                entry_fee=fill.fee,
                entry_slippage=fill.slippage_cost,
                entry_t=fill.t,
            )
            accepted += 1
            state.mark(fill_price)
            equity_curve.append(state.equity)
        elif signal.direction != 0:
            rejected += 1

    if state.position is not None:
        final_frame = frames[-1]
        position = state.position
        fill = simulate_fill(
            OrderIntent(
                t=final_frame.t,
                symbol=TARGET,
                action="CLOSE",
                side=position.side,
                quantity=position.quantity,
                reference_price=final_frame.prices[TARGET],
                reason="final_flatten",
            ),
            final_frame.prices[TARGET],
        )
        gross = position.side * (fill.fill_price - position.entry_price) * position.quantity
        fees = position.entry_fee + fill.fee
        slippage = position.entry_slippage + fill.slippage_cost
        net = gross - fees
        state.realized_pnl += net
        trades.append(
            {
                "entry_t": position.entry_t,
                "exit_t": fill.t,
                "side": position.side,
                "quantity": position.quantity,
                "gross_pnl": round(gross, 4),
                "fees": round(fees, 4),
                "slippage_cost": round(slippage, 4),
                "net_pnl": round(net, 4),
            }
        )
        state.position = None
        state.mark(final_frame.prices[TARGET])
        equity_curve.append(state.equity)

    summary = summarize(trades, equity_curve, accepted, rejected)
    summary["evidence_type"] = "synthetic_demo"
    summary["not_claimed"] = "real alpha or live performance"
    return {"summary": summary, "trades": trades}

