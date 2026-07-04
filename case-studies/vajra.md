# Vajra Personal Multi-Asset Research Platform

Vajra is my personal research and execution-infrastructure platform. It is not a company. This public case study is intentionally sanitized: it explains the system design, research process and evidence standard without revealing proprietary alpha rules, credentials, broker identifiers or raw order logs.

## Problem

Markets are not isolated. Indian sectors and instruments react to domestic conditions, but also to global sector moves, US/China/Japan/Korea context, crude oil, FX, macro regimes, options/futures positioning and broader risk appetite. I wanted a platform that could bring these inputs together, quantify relationships and convert research ideas into validated trading-system components.

## What I Built

Vajra connects the full research-to-execution path:

```text
market data
  -> feature engineering
  -> cross-market relationship analysis
  -> signal and regime models
  -> walk-forward / replay validation
  -> risk contracts
  -> order intents
  -> execution journals
  -> replay and post-trade analytics
```

The platform covers equities, futures, options and crypto research. It includes multi-horizon decision models for execution context, intraday signal selection, daily/weekly regime and theme selection, and monthly robustness/capital review.

## Research Surface

Public-safe research areas include:

- cross-asset signal discovery;
- market-transmission research between global and Indian markets;
- sector and macro context;
- momentum, reversal, mean reversion and volatility regimes;
- options features such as OI, IV, expiry, moneyness and call/put behavior;
- breadth and regime detection;
- execution-aware research and post-trade feedback.

Exact strategy rules and signal thresholds are omitted.

## Validation Evidence

Evidence discovered in private source artifacts includes:

- rolling walk-forward equity/futures research using completed-prior-data separation and a 730-day training lookback;
- one multi-year research report covering 70,013 simulated trades over 2020-01-01 to 2026-06-11, with reported win rate, profit factor, positive-month count, drawdown and capital tracking;
- crypto replay infrastructure consuming live-current signals and risk contracts;
- a sampled replay with 2,618 accepted trades, 2,613 closed trades and 468 symbols tracked;
- a paper-fill live-window simulation with 318 accepted/closed trades;
- execution-variant studies across 37 variants comparing fill assumptions, fees, fill rate, unresolved positions, side outcomes, Sharpe and drawdown;
- structured lifecycle journals for signals, risk decisions, order intents, smart-execution decisions, exchange journals and private socket events.

These are research, simulation, replay and system-activity artifacts. They are not presented as audited live performance.

## Engineering Notes

The platform uses Python for research/orchestration/replay, C++ for selected live matrix/feature/scoring paths, Redis for live state, PostgreSQL/SQLite for candles and archives, JSONL for lifecycle journals and Linux/AWS for runtime operations.

The engineering focus is on building the complete loop from ground level:

- raw data and market context;
- features and relationship discovery;
- validation and replay;
- risk and capital constraints;
- order lifecycle and execution evidence;
- feedback into research.

For a sanitized public illustration of this architecture pattern, see the runnable [Research-To-Execution Demo](../examples/research_to_execution_demo/README.md). The demo uses synthetic data and toy logic only.

## What This Demonstrates

Vajra is evidence of:

- ability to build full-stack quant infrastructure independently;
- ability to connect macro, cross-asset and instrument-level context;
- ability to separate research, simulation, replay and live-system activity;
- ability to design logs, contracts and reports that make trading-system behavior auditable;
- ability to think beyond one-dimensional signals while remaining implementation-oriented.

## What Is Not Claimed

- No audited live PnL claim.
- No institutional alpha claim.
- No disclosure of proprietary alpha rules.
- No raw order IDs, account details, credentials or broker secrets.
