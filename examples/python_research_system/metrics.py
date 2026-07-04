"""Metric helpers for validation and replay outputs."""

from __future__ import annotations

from math import sqrt


def max_drawdown(equity_curve: list[float]) -> float:
    peak = equity_curve[0]
    worst = 0.0
    for value in equity_curve:
        peak = max(peak, value)
        if peak:
            worst = min(worst, value / peak - 1.0)
    return worst


def profit_factor(pnls: list[float]) -> float:
    wins = sum(p for p in pnls if p > 0)
    losses = abs(sum(p for p in pnls if p < 0))
    if losses == 0:
        return 0.0 if wins == 0 else 999.0
    return wins / losses


def sharpe_like(pnls: list[float]) -> float:
    if len(pnls) < 2:
        return 0.0
    mean = sum(pnls) / len(pnls)
    variance = sum((p - mean) ** 2 for p in pnls) / (len(pnls) - 1)
    std = sqrt(variance)
    if std == 0:
        return 0.0
    return mean / std * sqrt(252.0)


def summarize_trades(trades: list[dict], equity_curve: list[float], accepted: int, rejected: int) -> dict:
    pnls = [float(t["net_pnl"]) for t in trades]
    wins = sum(1 for pnl in pnls if pnl > 0)
    fees = sum(float(t["fees"]) for t in trades)
    slippage = sum(float(t["slippage_cost"]) for t in trades)
    gross = sum(float(t["gross_pnl"]) for t in trades)
    net = sum(pnls)
    return {
        "trades": len(trades),
        "accepted_intents": accepted,
        "rejected_intents": rejected,
        "win_rate": round(wins / len(trades), 4) if trades else 0.0,
        "profit_factor": round(profit_factor(pnls), 4),
        "sharpe_like": round(sharpe_like(pnls), 4),
        "gross_pnl": round(gross, 4),
        "fees": round(fees, 4),
        "slippage_cost": round(slippage, 4),
        "net_pnl": round(net, 4),
        "max_drawdown": round(max_drawdown(equity_curve), 4),
        "final_equity": round(equity_curve[-1], 4),
    }
