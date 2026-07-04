"""Replay metric helpers for the public demo."""

from __future__ import annotations


def max_drawdown(equity_curve: list[float]) -> float:
    peak = equity_curve[0]
    worst = 0.0
    for value in equity_curve:
        peak = max(peak, value)
        if peak:
            worst = min(worst, value / peak - 1.0)
    return worst


def summarize(trades: list[dict], equity_curve: list[float], accepted: int, rejected: int) -> dict:
    gross_pnl = sum(t["gross_pnl"] for t in trades)
    fees = sum(t["fees"] for t in trades)
    slippage = sum(t["slippage_cost"] for t in trades)
    net_pnl = sum(t["net_pnl"] for t in trades)
    wins = sum(1 for t in trades if t["net_pnl"] > 0)
    return {
        "trades": len(trades),
        "accepted_intents": accepted,
        "rejected_intents": rejected,
        "win_rate": round(wins / len(trades), 4) if trades else 0.0,
        "gross_pnl": round(gross_pnl, 4),
        "fees": round(fees, 4),
        "slippage_cost": round(slippage, 4),
        "net_pnl": round(net_pnl, 4),
        "max_drawdown": round(max_drawdown(equity_curve), 4),
        "final_equity": round(equity_curve[-1], 4),
    }

