# Systems Notes

This page is the compact technical version of how I think about quant infrastructure. The public examples are synthetic, but the architecture reflects the systems I have worked on: research first, then risk, then execution.

## Research Layer

Python is the right tool for most of my research loop:

- load market and macro data;
- build completed-prior-data features;
- test cross-market relationships;
- run backtests and walk-forward studies;
- calculate Sharpe, drawdown, win rate, profit factor, fees, slippage and capital usage;
- produce reports that can be compared across strategy versions.

The research idea is broad by design. I want models that understand what is happening globally and locally before acting. Examples include oil versus Indian sectors, US/China/Japan/Korea sector behavior versus Indian sectors, Indian and global macro context, futures/options structure, volatility, sector rotation, risk appetite and mean-reversion/momentum regimes.

## Live Runtime

Live systems should be small, fast and explicit. My preference is:

- **C++ for live runtime:** sockets, order managers, risk managers, private-stream handlers, execution engines and hot-path state.
- **JSON contracts:** signals, risk decisions, order intents, execution events, position snapshots and journals.
- **Redis for hot state:** streams, queues, market data hashes, depth snapshots, positions, working orders and heartbeats.
- **PostgreSQL for durable state:** instruments, candles, Greeks, snapshots, reports, research outputs and EOD flushes.

The boundary is intentional: Python can research and simulate; C++ should own the live loop.

In my own naming, the live path maps naturally to components like `socket.cpp`, `risk.cpp`, order manager, risk manager, Redis writers/readers and PostgreSQL writers. The exact code is private, but the public example keeps the same shape: JSON in, risk authority, order intent, execution event, JSON out.

## Risk Authority

Risk should be an independent authority, not a helper function hidden inside a strategy. The risk layer should be able to reject or resize orders even when a signal is strong.

Controls I care about:

- global capital limits;
- segment capital limits;
- side-level exposure;
- symbol and strategy exposure;
- max active orders and max new orders;
- quote freshness and stale-data protection;
- drawdown and hard-exit controls;
- leverage and margin buffers;
- kill-switch style stop conditions.

This makes the system easier to reason about: signal generation proposes, risk decides, execution implements.

The important part is that risk has one authority. Strategies do not get to bypass it. Every order intent should be checked against global capital, segment capital, symbol exposure, side exposure and live state before it reaches execution.

## Execution Design

Execution needs to adapt to the market instead of blindly firing orders:

- check bid/ask, spread and depth before placing intent;
- reject stale quotes;
- cap slippage and price drift;
- lean price around bid, ask or mid depending on side and urgency;
- replace or adjust working orders after a time interval;
- split large exposure into smaller chunks;
- use ladder entries/exits where appropriate;
- track fills, rejects, fees, slippage and mark-to-market impact.

For exits, the same idea applies: take-profit, stop-loss, trailing exits, hard exits, time exits and position-aware adjustments should be controlled by state, not manual judgment.

The same framework should support adaptive entries and exits across timeframes: a signal can express urgency and confidence, risk can resize or reject it, and execution can adjust price, quantity or timing based on current liquidity and state.

## Low-Latency and Memory Discipline

The goal is not to call everything "HFT." The goal is to design live systems that respect latency and state.

Techniques I use or design around:

- keep active market state and working orders in memory;
- keep Redis as the hot shared state layer rather than querying a database in the execution path;
- use queues/streams to decouple market data, risk and order execution;
- use C++ atomics, mutexes and worker loops where live components need concurrency;
- batch or flush durable writes outside the hot path;
- keep JSON contracts small and explicit;
- use heartbeats and state snapshots so broken processes are visible quickly.

## Professional Systems Exposure

At GreyOak, my work is around research systems, market-intelligence tooling and internal context systems such as Horizon, Compass, Context-Intelligence and Ask-GreyOak.

At KIFS, the work was closer to trading-system mechanics: broker/API workflows, F2F conversion/reversion research, options analytics, tick/depth data, order lifecycle, execution constraints and risk-aware trading-system design.

At Greeksoft, I worked around broker-facing algo-trading platform workflows: broker connectivity, instrument mapping, market data, order placement, order status and execution flow.

## What This Repo Is Trying To Show

I want this repo to show that I can bring the full chain together:

1. Form a market hypothesis.
2. Quantify it with features and data.
3. Backtest and simulate it with costs.
4. Convert it into a risk-aware signal.
5. Pass it through an independent risk authority.
6. Generate an order intent.
7. Execute or simulate execution.
8. Replay the lifecycle and measure what happened.

That is the skill I am trying to build toward: not just writing strategies, and not just writing infrastructure, but connecting research, risk and execution into one system.
