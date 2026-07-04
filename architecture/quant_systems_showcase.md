# Quant Systems Showcase

This repo presents a public, synthetic version of the architecture I build toward: research produces explicit decisions, risk is an independent authority, and live runtime components communicate through small JSON contracts.

## System Shape

```text
market archives / synthetic market frames
        |
        v
Python research layer
  - feature engineering
  - signal scoring
  - backtest / replay
  - portfolio state
  - reports and dashboards
        |
        v
JSON contracts
  - signal
  - risk decision
  - order intent
  - execution event
  - portfolio state
  - replay summary
        |
        v
C++ runtime layer
  - queues
  - risk authority
  - order manager
  - adaptive limit pricing
  - execution journal
  - heartbeat / runtime state
        |
        v
post-trade evidence
  - fills
  - position updates
  - PnL / drawdown
  - replayable lifecycle events
```

## Python Layer

Python owns the research and control-plane surface:

- build lag-safe features from market and context inputs;
- generate synthetic signals from feature snapshots;
- run deterministic replay with fees, slippage and position accounting;
- evaluate pre-trade risk before order intent creation;
- output lifecycle events that resemble production logs without exposing real strategy rules.

The public demo is in `examples/research_to_execution_demo/`.

## JSON Layer

JSON is the interface between research, risk and runtime. The examples in `contracts/` show the public shape of the messages:

- `signal.json` represents a research output;
- `risk_contract.json` represents limits owned by risk;
- `risk_decision.json` records approve/reject output;
- `order_intent.json` represents the instruction passed to execution;
- `execution_event.json` records fill accounting;
- `portfolio_state.json` records current state;
- `replay_summary.json` records aggregate evidence.

## C++ Layer

C++ owns the live-runtime shape:

- queue signals into risk evaluation;
- reserve risk budget before order intent creation;
- build adaptive limit prices from contract limits;
- pass accepted intents to the execution worker;
- emit JSON events for risk decisions, order intents, fills, heartbeat and runtime state.

The public demo is in `examples/cpp_live_runtime_demo/`.

## Boundary Discipline

The important design decision is the separation of responsibilities:

- research proposes;
- risk accepts, rejects or resizes;
- execution implements;
- journals make every step replayable.

That is the same discipline needed in a serious trading system, even when this repo uses synthetic market data and public-safe logic.
