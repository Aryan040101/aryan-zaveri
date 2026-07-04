# Aryan Zaveri

**Quant Developer | Trading Systems | Research Infrastructure | Execution-Aware Systems**

[LinkedIn](https://www.linkedin.com/in/aryan-zaveri0401/) · [One-Page Resume](resume/Aryan_Zaveri_Quant_Developer_One_Page_Resume.pdf) · [Two-Page CV](resume/Aryan_Zaveri_Quant_Developer_Two_Page_CV.pdf)

I build trading systems from the ground up: market data, feature engineering, strategy research, backtests, risk checks, order intent generation, execution tracking, replay, and post-trade analysis.

My strongest work is end-to-end quant infrastructure. I use Python for the research and control-plane layer: data loading, feature engineering, signal research, ML-style experiments, backtesting, walk-forward validation, replay, reporting, monitoring and orchestration. I use C++ for live/runtime systems where latency, memory use, sockets, queues, order state and risk authority matter. The systems communicate through JSON contracts, keep hot state in Redis, and persist historical/research state into PostgreSQL or Timescale-style stores.

The C++ side is not a small add-on. It is the live/runtime layer: market sockets, private order sockets, risk managers, order managers, signal bridges, position trackers, Redis hot-state workers, PostgreSQL writers, replay/parity tools and service processes that can run under Linux/systemd.

The Python side is also substantial. It is where I build feature tables, model pipelines, options/equity/crypto research flows, no-lookahead backtests, walk-forward studies, risk grids, portfolio comparisons, dashboards, data repair jobs, Redis/Postgres writers and operational monitors.

## What I Build

- **Research and backtesting:** factor studies, feature pipelines, walk-forward tests, replay engines, simulation reports and metric extraction.
- **Python research systems:** pandas/numpy feature pipelines, model training, threshold search, no-lookahead validation, replay, dashboards, state writers and research reports.
- **Live trading runtime:** C++ socket handlers, private streams, order managers, risk managers, working-order state, execution journals, heartbeats, recovery loops and service daemons.
- **Risk authority:** one independent risk layer that controls global capital, segment capital, side limits, symbol limits, active order limits and hard exits.
- **Adaptive execution:** quote freshness checks, spread/slippage gates, price leaning, replace/adjust loops, chunking, ladder exits and position-aware adjustments.
- **Cross-market research:** linking Indian markets with global indices, crude oil, FX, macro data, sector themes, options/futures behavior and crypto risk appetite.
- **Storage and state:** Redis streams/hashes for hot state and queues; PostgreSQL writers for durable candles, instruments, Greeks, analytics, snapshots and research outputs.

This repo is a public portfolio version: runnable code, architecture notes and resumes that focus on systems design, engineering judgment and research-to-execution thinking.

## Code Map

- [examples/cpp_trading_runtime/](examples/cpp_trading_runtime): modular C++20 runtime with hot state, risk authority, order manager, worker queues, adaptive pricing and journals.
- [architecture/quant_systems_showcase.md](architecture/quant_systems_showcase.md): Python/C++ system architecture and data flow.
- [examples/research_to_execution_demo/](examples/research_to_execution_demo): Python research-to-execution replay with synthetic market data, lag-safe features, risk checks, fills and lifecycle events.
- [examples/cpp_live_runtime_demo/](examples/cpp_live_runtime_demo): compact single-file C++ queue/risk/order runtime demo.
- [contracts/](contracts): public message examples for signals, risk decisions, order intents, execution events, portfolio state and replay summaries.

## Public Examples

### Python Research / Backtest Demo

The Python example is deliberately offline. It shows how I think about completed-prior-data features, signal scoring, pre-trade risk, deterministic fills, fees, slippage, replay accounting, portfolio state and JSON lifecycle events.

```bash
python3 examples/research_to_execution_demo/run_demo.py | python3 -m json.tool
```

The larger Python shape includes research scripts, feature builders, options model pipelines, equity/futures portfolio analysis, crypto movement/relationship engines, Redis/Postgres data services, FastAPI-style monitors and scheduled reporting jobs.

### C++ Trading Runtime Demo

The modular C++ example is the main runtime showcase. It splits the system into hot state, risk authority, order manager, queueing and journal components.

```bash
g++ -std=c++20 -O2 -pthread -Iexamples/cpp_trading_runtime/include examples/cpp_trading_runtime/src/*.cpp -o /tmp/cpp_trading_runtime
/tmp/cpp_trading_runtime | python3 -m json.tool
```

Or with CMake:

```bash
cmake -S examples/cpp_trading_runtime -B /tmp/cpp_trading_runtime_build
cmake --build /tmp/cpp_trading_runtime_build
/tmp/cpp_trading_runtime_build/cpp_trading_runtime | python3 -m json.tool
```

The larger runtime shape behind this is closer to a production trading stack: socket processes, risk manager, order manager, market-state cache, Redis stream consumers, PostgreSQL persistence, heartbeats, snapshots, replay tooling and Linux services.

### Compact C++ Runtime Shape

The compact C++ example is a small public model of the live path: signals, risk limits, an in-memory queue, an independent risk authority, adaptive order intent generation and execution journaling.

```bash
g++ -std=c++20 -O2 -pthread examples/cpp_live_runtime_demo/live_runtime_demo.cpp -o /tmp/live_runtime_demo
/tmp/live_runtime_demo | python3 -m json.tool
```

### Message Contract Validation

The message examples are validated in CI.

```bash
python3 tools/validate_contract_examples.py
```

## Flagship Work: Vajra

**Vajra** is my personal multi-asset research and trading infrastructure platform. It is not a company.

The core idea is simple: markets do not move in isolation. Vajra is built to connect Indian sectors, global indices, crude oil, FX, macro context, options/futures structure and broader risk appetite into models that can be researched, backtested, replayed and wired into risk-aware execution.

The public version focuses on the architecture: Python for research, validation, analytics, monitoring and orchestration; C++ for live sockets/risk/order runtimes; JSON contracts between components; Redis for hot state; PostgreSQL for durable storage; and a single risk authority before execution.

The point is not to show one isolated strategy. It is to show that I can quantify relationships, test them, simulate them with costs, and connect the surviving ideas to execution systems.

## Professional Experience

### GreyOak Capital — Quantitative Developer

I work on quantitative research systems, market-intelligence infrastructure and research-facing tooling. My work touches Horizon, Compass, Context-Intelligence and Ask-GreyOak style systems that bring market context, internal data flows, dashboards, WebSocket/data contracts and analyst-facing interfaces together.

### KIFS Trade Capital — Quantitative / Algorithmic Trading Development

Worked across algorithmic trading development, broker/API workflows, intraday market-data processing, options analytics and F2F conversion/reversion research. The work gave me strong exposure to order lifecycle mechanics, tick/depth data, execution constraints, latency-aware design, risk checks and trade-quality analysis.

### Greeksoft Technologies — Algorithmic Trading Internship

Worked around broker-facing algo-trading platform workflows: how brokers connect, how instruments are mapped, how market data arrives, how orders are placed, how order status is tracked and how execution flow is represented in a platform.

## Technical Stack

Python · pandas · numpy · scikit-learn style workflows · C++ · SQL · Shell · Linux · AWS · Git · Docker · Redis · PostgreSQL · FastAPI-style services · WebSockets · REST APIs · JSON contracts · market data · backtesting · replay · pre-trade risk · order lifecycle · execution analytics

## Deeper Technical Notes

Read [SYSTEMS.md](SYSTEMS.md) for the technical breakdown of the Python research layer, C++ live runtime, risk authority, Redis/Postgres design, adaptive execution and current improvement roadmap.

## Current Direction

I am optimizing for quant developer and research engineering roles where the work needs both market understanding and production-quality systems thinking: building models, testing them, wiring them into risk-aware execution, and knowing exactly where research ends and live trading begins.
