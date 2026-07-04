# Quant Systems Showcase

This repo presents a public, synthetic version of the architecture I build toward: research produces explicit decisions, risk is an independent authority, and live runtime components are implemented as narrow C++ services with clear message boundaries.

## System Shape

```text
market archives / synthetic market frames
        |
        v
Python research layer
  - market data
  - feature engineering
  - signal scoring
  - walk-forward validation
  - risk / portfolio simulation
  - replay
  - reports and dashboards
        |
        v
message contracts
  - signal
  - risk decision
  - order intent
  - execution event
  - portfolio state
  - replay summary
        |
        v
C++ runtime layer
  - hot state store
  - worker queues
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

Python owns the research and control-plane surface. The main public example is `examples/python_research_system/`, which uses a modular layout:

- `market_data.py` generates deterministic multi-market context;
- `features.py` builds lag-safe cross-market features;
- `signals.py` turns feature rows into scored signal candidates;
- `validation.py` runs walk-forward threshold selection;
- `risk.py` owns pre-trade approval/rejection;
- `portfolio.py` tracks equity, drawdown and positions;
- `execution.py` builds intents and simulates fills;
- `replay.py` ties signal, risk, execution and portfolio accounting together;
- `reports.py` assembles the research report.

The compact Python replay remains in `examples/research_to_execution_demo/` for quick inspection.

## Message Layer

The message examples in `contracts/` show the public shape of the interfaces between research, risk and runtime:

- `signal.json` represents a research output;
- `risk_contract.json` represents limits owned by risk;
- `risk_decision.json` records approve/reject output;
- `order_intent.json` represents the instruction passed to execution;
- `execution_event.json` records fill accounting;
- `portfolio_state.json` records current state;
- `replay_summary.json` records aggregate evidence.

## C++ Layer

C++ owns the live-runtime shape. The main public example is `examples/cpp_trading_runtime/`, which uses a modular layout instead of one script:

- `runtime_types.hpp` defines signals, quotes, limits, decisions, orders, fills and positions;
- `blocking_queue.hpp` provides the worker-queue primitive;
- `hot_state.cpp` models Redis-like hot state for quotes, working orders and positions;
- `risk_authority.cpp` owns quote freshness, confidence, notional and active-order gates;
- `order_manager.cpp` builds/adapts order intents and simulates fills;
- `journal.cpp` emits replayable lifecycle events;
- `trading_runtime_main.cpp` wires the service loop together.

The compact single-file demo remains in `examples/cpp_live_runtime_demo/` for quick inspection.

## Boundary Discipline

The important design decision is the separation of responsibilities:

- research proposes;
- risk accepts, rejects or resizes;
- execution implements;
- journals make every step replayable.

That is the same discipline needed in a serious trading system, even when this repo uses synthetic market data and public-safe logic.
