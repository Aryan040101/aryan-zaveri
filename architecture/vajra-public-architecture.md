# Vajra Public Architecture

This is a sanitized architecture view. It excludes proprietary strategy rules, exact thresholds, private datasets, broker identifiers, credentials and raw trading logs.

```text
External / Market Context
  - Indian equities, futures and options
  - Crypto markets
  - Global indices and sectors
  - Crude oil, FX and macro context
  - Broker/exchange market data

        |
        v

Data & State Layer
  - Historical candles and archives
  - Instrument/reference mappings
  - Live state and market snapshots
  - JSONL lifecycle journals

        |
        v

Research Layer
  - Feature engineering
  - Cross-market relationship analysis
  - Regime and breadth studies
  - Options/futures feature studies
  - Walk-forward and simulation reports

        |
        v

Decision Layer
  - Multi-horizon signal scoring
  - Risk-state evaluation
  - Capital and exposure constraints
  - Strategy/risk contracts

        |
        v

Execution Evidence Layer
  - Risk decisions
  - Order intents
  - Smart-execution journals
  - Exchange/private-socket journals
  - Replay and post-trade analytics
```

## Design Principles

- Build from raw market data upward.
- Treat markets as connected systems, not isolated tickers.
- Separate research, simulation, replay, paper/live activity and audited performance.
- Keep every major decision path journaled.
- Feed execution and replay evidence back into research.

## Public-Safe Technology View

- Python for research, orchestration and replay.
- C++ for selected live matrix/feature/scoring paths.
- Redis for live state.
- PostgreSQL/SQLite for candles and archives.
- JSONL for lifecycle journals.
- Linux/AWS for runtime operations.

## Omitted By Design

- Exact strategy rules and alpha logic.
- Broker credentials and account identifiers.
- Raw order IDs and raw execution logs.
- Employer-sensitive implementation details.
- Private data sources and internal infrastructure paths.

