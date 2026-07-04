# Systems Notes

This page is the compact technical version of how I think about quant infrastructure: research first, then risk, then execution.

## Research Layer

Python is the right tool for most of my research loop:

- load market and macro data;
- build completed-prior-data features;
- test cross-market relationships;
- run backtests and walk-forward studies;
- calculate Sharpe, drawdown, win rate, profit factor, fees, slippage and capital usage;
- produce reports that can be compared across strategy versions.

The research idea is broad by design. I want models that understand what is happening globally and locally before acting. Examples include oil versus Indian sectors, US/China/Japan/Korea sector behavior versus Indian sectors, Indian and global macro context, futures/options structure, volatility, sector rotation, risk appetite and mean-reversion/momentum regimes.

## Python Research Inventory

I do not treat Python as just glue code. It is the research operating layer:

- **Feature engineering:** OHLCV features, returns, realized volatility, momentum, RSI, volume ratios, futures basis, IV rank, IV term slope, PCR/OI, max-pain and gamma-distance style context, breadth, macro inputs, sector relationships and BTC-relative behavior.
- **Signal research:** rule families, statistical models, rolling models, Kalman-style trend logic, LightGBM-style ensembles, options call/put selection, equity/futures side books and crypto relationship candidates.
- **Validation:** completed-prior-data features, no-lookahead signal generation, train/test windows, walk-forward selection, out-of-sample metrics, replay, paper-fill simulation, fee/slippage assumptions and quality gates.
- **Portfolio research:** green/red side books, combined portfolio comparisons, deployed-margin limits, sector caps, active-position limits, daily loss pauses, MTM curves, month summaries and capital-required views.
- **Data services:** Redis stream consumers, Redis hashes/queues, bar writers, L1/L2 writers, PostgreSQL candle writers, instrument tables, feature-table builders and retention/repair jobs.
- **Options research:** dataset builders, model bundles, threshold search, replay inference, live inference, feature-table daemons, Postgres inference storage and monitor views.
- **Monitoring and reporting:** FastAPI-style dashboards, spread views, backfill-healing views, market briefs, operational reports, lifecycle journals and research-output inspection.

The practical split is:

```text
Python: research, features, validation, reports, orchestration, monitoring
C++: sockets, hot state, risk authority, order runtime, execution journals
Redis: live shared state and queues
PostgreSQL: durable market/research/execution records
JSON: contracts between components
```

This lets research move quickly without hiding live-trading responsibilities inside notebooks or ad hoc scripts.

## Live Runtime

Live systems should be small, fast and explicit. My preference is:

- **C++ for live runtime:** market sockets, private-stream handlers, order managers, risk managers, position trackers, signal bridges, execution engines and hot-path state.
- **JSON contracts:** signals, risk decisions, order intents, execution events, position snapshots and journals.
- **Redis for hot state:** streams, queues, market data hashes, depth snapshots, positions, working orders and heartbeats.
- **PostgreSQL for durable state:** instruments, candles, Greeks, snapshots, reports, order/position history, research outputs and EOD flushes.

The boundary is intentional: Python can research and simulate; C++ should own the live loop.

In my own naming, the live path maps naturally to components like `socket.cpp`, `risk.cpp`, order manager, risk manager, Redis writers/readers and PostgreSQL writers. The public example keeps the same shape: JSON in, risk authority, order intent, execution event, JSON out.

## C++ Runtime Inventory

The C++ work is best understood as a set of cooperating runtime services, not one script:

- **Socket layer:** exchange market sockets, broker/private sockets, reconnect loops, heartbeat handling, depth/top-of-book state, JSON snapshots and event journals.
- **Risk layer:** independent risk manager/risk-governor processes that read signal intent, live positions, account context, market state and capital constraints before approving, resizing or rejecting action.
- **Order layer:** order manager and smart-execution style flows that consume approved intents, check quote freshness and slippage, maintain working-order state and write order/execution journals.
- **State layer:** Redis streams/hashes for hot market state, active orders, positions, heartbeats and inter-process queues; PostgreSQL writers for durable records that should not sit in the execution path.
- **Research-to-live layer:** replay/parity tools, live-matrix scoring, paper-fill simulation, exit replay, strategy contract promotion and weekly rule/model tooling.
- **Deployment layer:** CMake-built services, Linux/systemd process boundaries, memory guard behavior, runtime logs and operational heartbeats.

The design goal is to keep each process narrow. A socket process should not decide portfolio risk. A strategy should not bypass the risk authority. A database writer should not block order routing.

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

## Order And Risk Flow

The flow I aim for is:

```text
market data / features
        |
        v
signal candidate
        |
        v
risk authority
        |
        +--> reject / resize / wait
        |
        v
order intent
        |
        v
order manager / execution engine
        |
        v
exchange or broker path
        |
        v
fills, rejects, positions, PnL, replay journals
```

This is why the C++ layer matters. The live path needs clear ownership of sockets, queueing, active memory state, risk decisions, order state and journaled outcomes.

## Low-Latency and Memory Discipline

The goal is not to call everything "HFT." The goal is to design live systems that respect latency and state.

Techniques I use or design around:

- keep active market state and working orders in memory;
- keep Redis as the hot shared state layer rather than querying a database in the execution path;
- use queues/streams to decouple market data, risk and order execution;
- use C++ atomics, mutexes and worker loops where live components need concurrency;
- use small process-local caches for instruments, quotes, risk contracts and active orders;
- keep order/risk communication event-driven through streams and explicit JSON contracts;
- batch or flush durable writes outside the hot path;
- keep JSON contracts small and explicit;
- use heartbeats and state snapshots so broken processes are visible quickly.

## Professional Systems Exposure

At GreyOak, my work is around research systems, market-intelligence tooling and internal context systems such as Horizon, Compass, Context-Intelligence and Ask-GreyOak.

At KIFS, the work was closer to trading-system mechanics: broker/API workflows, F2F conversion/reversion research, options analytics, tick/depth data, order lifecycle, execution constraints and risk-aware trading-system design.

At Greeksoft, I worked around broker-facing algo-trading platform workflows: broker connectivity, instrument mapping, market data, order placement, order status and execution flow.

## What This Repo Is Trying To Show

I want this repo to show the full chain: hypothesis, data, features, backtest, risk decision, order intent, execution or replay, and measurement.

That is the skill I am building toward: not just writing strategies, and not just writing infrastructure, but connecting research, risk and execution into one system.
