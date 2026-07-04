"""Portfolio state and accounting for synthetic replay."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Position:
    symbol: str
    side: int
    quantity: int
    entry_price: float
    entry_t: int
    fees: float = 0.0


@dataclass
class PortfolioState:
    starting_equity: float = 100_000.0
    realized_pnl: float = 0.0
    equity: float = 100_000.0
    peak_equity: float = 100_000.0
    current_drawdown: float = 0.0
    positions: dict[str, Position] = field(default_factory=dict)

    def mark(self, prices: dict[str, float]) -> float:
        unrealized = 0.0
        for position in self.positions.values():
            price = prices[position.symbol]
            unrealized += position.side * (price - position.entry_price) * position.quantity
        self.equity = self.starting_equity + self.realized_pnl + unrealized
        self.peak_equity = max(self.peak_equity, self.equity)
        self.current_drawdown = self.equity / self.peak_equity - 1.0
        return self.equity

    def snapshot(self) -> dict:
        return {
            "equity": round(self.equity, 4),
            "peak_equity": round(self.peak_equity, 4),
            "current_drawdown": round(self.current_drawdown, 4),
            "realized_pnl": round(self.realized_pnl, 4),
            "positions": {
                symbol: {
                    "side": "BUY" if pos.side > 0 else "SELL",
                    "quantity": pos.quantity,
                    "entry_price": round(pos.entry_price, 4),
                    "entry_t": pos.entry_t,
                }
                for symbol, pos in self.positions.items()
            },
        }
