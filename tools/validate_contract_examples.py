#!/usr/bin/env python3
"""Validate public JSON contract examples.

The checks are intentionally small and dependency-free. They prove that the
portfolio repo treats JSON as an interface between research, risk and runtime
components rather than as loose documentation.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "contracts"

REQUIRED_FIELDS: dict[str, set[str]] = {
    "signal.json": {
        "contract",
        "version",
        "event",
        "source",
        "symbol",
        "market",
        "timeframe",
        "side",
        "score",
        "confidence",
        "features",
    },
    "risk_contract.json": {
        "contract",
        "version",
        "global_capital_limit",
        "cash_segment_limit",
        "derivatives_segment_limit",
        "max_order_notional",
        "max_drawdown",
        "min_confidence",
        "max_slippage_bps",
    },
    "risk_decision.json": {
        "contract",
        "version",
        "event",
        "symbol",
        "side",
        "accepted",
        "reason",
        "quantity",
        "projected_notional",
        "checks",
    },
    "order_intent.json": {
        "contract",
        "version",
        "event",
        "symbol",
        "side",
        "action",
        "quantity",
        "reference_price",
        "limit_price",
        "reason",
    },
    "execution_event.json": {
        "contract",
        "version",
        "event",
        "symbol",
        "side",
        "action",
        "quantity",
        "reference_price",
        "fill_price",
        "fee",
        "slippage_cost",
        "source",
    },
    "portfolio_state.json": {
        "contract",
        "version",
        "event",
        "equity",
        "peak_equity",
        "current_drawdown",
        "realized_pnl",
        "open_position",
    },
    "replay_summary.json": {
        "contract",
        "version",
        "event",
        "evidence_type",
        "trades",
        "accepted_intents",
        "rejected_intents",
        "win_rate",
        "gross_pnl",
        "fees",
        "slippage_cost",
        "net_pnl",
        "max_drawdown",
        "final_equity",
    },
}


def load_contract(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{path.name}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise AssertionError(f"{path.name}: expected JSON object")
    return data


def require_number(data: dict[str, Any], path: Path, field: str) -> None:
    value = data.get(field)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise AssertionError(f"{path.name}: {field} must be numeric")


def validate_one(path: Path, required: set[str]) -> None:
    data = load_contract(path)
    missing = sorted(required - data.keys())
    if missing:
        raise AssertionError(f"{path.name}: missing fields: {', '.join(missing)}")
    if data.get("version") != "public.v1":
        raise AssertionError(f"{path.name}: version must be public.v1")
    if data.get("side") is not None and data["side"] not in {"BUY", "SELL"}:
        raise AssertionError(f"{path.name}: side must be BUY or SELL")
    if data.get("action") is not None and data["action"] not in {"OPEN", "CLOSE"}:
        raise AssertionError(f"{path.name}: action must be OPEN or CLOSE")
    for field in [
        "score",
        "confidence",
        "quantity",
        "projected_notional",
        "reference_price",
        "limit_price",
        "fill_price",
        "fee",
        "slippage_cost",
        "equity",
        "peak_equity",
        "current_drawdown",
        "realized_pnl",
        "trades",
        "accepted_intents",
        "rejected_intents",
        "win_rate",
        "gross_pnl",
        "net_pnl",
        "max_drawdown",
        "final_equity",
        "global_capital_limit",
        "cash_segment_limit",
        "derivatives_segment_limit",
        "max_order_notional",
        "max_drawdown",
        "min_confidence",
        "max_slippage_bps",
    ]:
        if field in data:
            require_number(data, path, field)


def main() -> int:
    failures: list[str] = []
    for name, required in REQUIRED_FIELDS.items():
        path = CONTRACTS / name
        if not path.exists():
            failures.append(f"missing contract file: {name}")
            continue
        try:
            validate_one(path, required)
        except AssertionError as exc:
            failures.append(str(exc))

    extra = sorted(p.name for p in CONTRACTS.glob("*.json") if p.name not in REQUIRED_FIELDS)
    if extra:
        failures.append("unexpected contract files: " + ", ".join(extra))

    if failures:
        print("contract validation failed:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1

    print("contract examples ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
