# Research-To-Execution Demo

This is a sanitized public demo of a small trading-system pipeline. It uses synthetic market data and toy signal logic. It is not Vajra source code, not a real alpha model and not live trading infrastructure.

## What It Demonstrates

```text
synthetic market data
  -> lag-safe feature generation
  -> toy signal score
  -> pre-trade risk gate
  -> order intent
  -> deterministic fill simulation
  -> replay ledger
  -> PnL / fees / drawdown summary
```

The goal is to show engineering structure: how research output can be carried into risk checks, order lifecycle objects, execution accounting and replay evidence.

## Run

From the repository root:

```bash
python3 examples/research_to_execution_demo/run_demo.py
```

Expected output is a deterministic JSON summary with fields such as:

- `trades`
- `accepted_intents`
- `rejected_intents`
- `gross_pnl`
- `fees`
- `slippage_cost`
- `net_pnl`
- `max_drawdown`
- `final_equity`

## Test

```bash
python3 -m unittest discover examples/research_to_execution_demo/tests
```

## Boundaries

- Uses synthetic data only.
- Uses toy signal logic only.
- Does not include broker integrations.
- Does not include proprietary alpha rules.
- Does not claim live or audited performance.

