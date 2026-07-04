"""Research-to-execution replay with portfolio/risk separation."""

from __future__ import annotations

from execution import OrderIntent, adaptive_limit, simulate_fill
from features import build_feature_row
from market_data import MarketSlice, SYMBOLS
from metrics import summarize_trades
from portfolio import PortfolioState, Position
from risk import RiskLimits, evaluate
from signals import build_signal


def _side_name(side: int) -> str:
    return "BUY" if side > 0 else "SELL"


def _should_close(position: Position, signal_side: int, t: int, max_hold: int) -> bool:
    if signal_side and signal_side != position.side:
        return True
    return t - position.entry_t >= max_hold


def run_replay(
    slices: list[MarketSlice],
    *,
    threshold: float,
    limits: RiskLimits | None = None,
    start_index: int = 24,
    end_index: int | None = None,
    max_hold: int = 12,
) -> dict:
    limits = limits or RiskLimits()
    end_index = end_index if end_index is not None else len(slices) - 1
    state = PortfolioState()
    trades: list[dict] = []
    events: list[dict] = []
    equity_curve = [state.starting_equity]
    accepted = 0
    rejected = 0
    target = SYMBOLS["target"]

    for index in range(start_index, end_index):
        current = slices[index]
        next_bar = slices[index + 1]
        decision_price = current.closes[target]
        fill_price = next_bar.closes[target]
        state.mark(current.closes)
        equity_curve.append(state.equity)

        row = build_feature_row(slices, index)
        signal = build_signal(row, threshold)
        if signal.side != 0:
            events.append(
                {
                    "event": "signal_generated",
                    "t": signal.t,
                    "symbol": signal.symbol,
                    "side": _side_name(signal.side),
                    "score": signal.score,
                    "confidence": signal.confidence,
                    "reason": signal.reason,
                }
            )

        position = state.positions.get(target)
        if position is not None and _should_close(position, signal.side, current.t, max_hold):
            intent = OrderIntent(
                t=next_bar.t,
                symbol=target,
                action="CLOSE",
                side=position.side,
                quantity=position.quantity,
                reference_price=decision_price,
                limit_price=adaptive_limit(-position.side, decision_price),
                reason="opposite_signal_or_time_exit",
            )
            fill = simulate_fill(intent, fill_price)
            gross = position.side * (fill.fill_price - position.entry_price) * position.quantity
            fees = position.fees + fill.fee
            slippage = fill.slippage_cost
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
            del state.positions[target]
            events.append({"event": "position_closed", "t": fill.t, "net_pnl": round(net, 4)})
            state.mark(next_bar.closes)
            equity_curve.append(state.equity)

        decision = evaluate(signal, state, decision_price, limits)
        if signal.side != 0:
            events.append(
                {
                    "event": "risk_decision",
                    "t": signal.t,
                    "symbol": signal.symbol,
                    "accepted": decision.accepted,
                    "reason": decision.reason,
                    "quantity": decision.quantity,
                    "projected_notional": round(decision.projected_notional, 4),
                }
            )
        if decision.accepted:
            intent = OrderIntent(
                t=next_bar.t,
                symbol=target,
                action="OPEN",
                side=signal.side,
                quantity=decision.quantity,
                reference_price=decision_price,
                limit_price=adaptive_limit(signal.side, decision_price),
                reason=decision.reason,
            )
            events.append(
                {
                    "event": "order_intent",
                    "t": intent.t,
                    "symbol": intent.symbol,
                    "side": _side_name(intent.side),
                    "quantity": intent.quantity,
                    "reference_price": round(intent.reference_price, 4),
                    "limit_price": round(intent.limit_price, 4),
                }
            )
            fill = simulate_fill(intent, fill_price)
            state.realized_pnl -= fill.fee
            state.positions[target] = Position(target, signal.side, decision.quantity, fill.fill_price, fill.t, fill.fee)
            events.append(
                {
                    "event": "execution_fill",
                    "t": fill.t,
                    "symbol": fill.symbol,
                    "side": _side_name(fill.side),
                    "quantity": fill.quantity,
                    "fill_price": fill.fill_price,
                    "fee": fill.fee,
                    "slippage_cost": fill.slippage_cost,
                }
            )
            accepted += 1
            state.mark(next_bar.closes)
            equity_curve.append(state.equity)
        elif signal.side != 0:
            rejected += 1

    if target in state.positions:
        final = slices[end_index]
        position = state.positions[target]
        fill = simulate_fill(
            OrderIntent(final.t, target, "CLOSE", position.side, position.quantity, final.closes[target], final.closes[target], "final_flatten"),
            final.closes[target],
        )
        gross = position.side * (fill.fill_price - position.entry_price) * position.quantity
        fees = position.fees + fill.fee
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
                "slippage_cost": round(fill.slippage_cost, 4),
                "net_pnl": round(net, 4),
            }
        )
        del state.positions[target]
        state.mark(final.closes)
        equity_curve.append(state.equity)

    summary = summarize_trades(trades, equity_curve, accepted, rejected)
    summary["evidence_type"] = "synthetic_research_system"
    return {
        "summary": summary,
        "portfolio_state": state.snapshot(),
        "events": events,
        "trades": trades,
    }
