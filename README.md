# Aryan Zaveri

**Quant Developer | Trading Systems | Research Infrastructure | Execution-Aware Systems**

[LinkedIn](https://www.linkedin.com/in/aryan-zaveri0401/) · [One-Page Resume](resume/Aryan_Zaveri_Quant_Developer_One_Page_Resume.pdf) · [Two-Page CV](resume/Aryan_Zaveri_Quant_Developer_Two_Page_CV.pdf)

I build trading systems from the ground up: market data, feature engineering, strategy research, backtests, risk checks, order intent generation, execution tracking, replay, and post-trade analysis.

My strongest work is end-to-end quant infrastructure. I use Python mainly for research, backtesting, analytics and reports. I use C++ for live/runtime systems where latency, memory use, sockets, queues, order state and risk authority matter. The systems communicate through JSON contracts, keep hot state in Redis, and persist historical/research state into PostgreSQL or Timescale-style stores.

The C++ side is not a small add-on. It is the live/runtime layer: market sockets, private order sockets, risk managers, order managers, signal bridges, position trackers, Redis hot-state workers, PostgreSQL writers, replay/parity tools and service processes that can run under Linux/systemd.

## What I Build

- **Research and backtesting:** factor studies, feature pipelines, walk-forward tests, replay engines, simulation reports and metric extraction.
- **Live trading runtime:** C++ socket handlers, private streams, order managers, risk managers, working-order state, execution journals, heartbeats, recovery loops and service daemons.
- **Risk authority:** one independent risk layer that controls global capital, segment capital, side limits, symbol limits, active order limits and hard exits.
- **Adaptive execution:** quote freshness checks, spread/slippage gates, price leaning, replace/adjust loops, chunking, ladder exits and position-aware adjustments.
- **Cross-market research:** linking Indian markets with global indices, crude oil, FX, macro data, sector themes, options/futures behavior and crypto risk appetite.
- **Storage and state:** Redis streams/hashes for hot state and queues; PostgreSQL writers for durable candles, instruments, Greeks, analytics, snapshots and research outputs.

This repo is a public portfolio version: architecture notes, compact demos and resumes that focus on systems design, engineering judgment and research-to-execution thinking.

## Public Examples

### Python Research / Backtest Demo

The Python example is deliberately offline. It shows how I think about completed-prior-data features, signal scoring, pre-trade risk, deterministic fills, fees, slippage, replay accounting and summary metrics.

```bash
python3 examples/research_to_execution_demo/run_demo.py
```

### C++ Live Runtime Shape

The C++ example is a small public model of the live path: JSON signals, JSON risk contracts, an in-memory queue, an independent risk authority, adaptive order intent generation and execution journaling.

```bash
g++ -std=c++20 -O2 -pthread examples/cpp_live_runtime_demo/live_runtime_demo.cpp -o /tmp/live_runtime_demo
/tmp/live_runtime_demo
```

The larger runtime shape behind this is closer to a production trading stack: socket processes, risk manager, order manager, market-state cache, Redis stream consumers, PostgreSQL persistence, heartbeats, snapshots, replay tooling and Linux services.

## Flagship Work: Vajra

**Vajra** is my personal multi-asset research and trading infrastructure platform. It is not a company.

The core idea is simple: markets do not move in isolation. Vajra is built to connect Indian sectors, global indices, crude oil, FX, macro context, options/futures structure and broader risk appetite into models that can be researched, backtested, replayed and wired into risk-aware execution.

The public version focuses on the architecture: Python for research and backtesting, C++ for live sockets/risk/order runtimes, JSON contracts between components, Redis for hot state, PostgreSQL for durable storage and a single risk authority before execution.

The point is not to show one isolated strategy. It is to show that I can quantify relationships, test them, simulate them with costs, and connect the surviving ideas to execution systems.

## Professional Experience

### GreyOak Capital — Quantitative Developer

I work on quantitative research systems, market-intelligence infrastructure and research-facing tooling. My work touches Horizon, Compass, Context-Intelligence and Ask-GreyOak style systems that bring market context, internal data flows, dashboards, WebSocket/data contracts and analyst-facing interfaces together.

### KIFS Trade Capital — Quantitative / Algorithmic Trading Development

Worked across algorithmic trading development, broker/API workflows, intraday market-data processing, options analytics and F2F conversion/reversion research. The work gave me strong exposure to order lifecycle mechanics, tick/depth data, execution constraints, latency-aware design, risk checks and trade-quality analysis.

### Greeksoft Technologies — Algorithmic Trading Internship

Worked around broker-facing algo-trading platform workflows: how brokers connect, how instruments are mapped, how market data arrives, how orders are placed, how order status is tracked and how execution flow is represented in a platform.

## Technical Stack

Python · C++ · SQL · Shell · Linux · AWS · Git · Docker · Redis · PostgreSQL · WebSockets · REST APIs · JSON contracts · market data · backtesting · replay · pre-trade risk · order lifecycle · execution analytics

## Deeper Technical Notes

Read [SYSTEMS.md](SYSTEMS.md) for the technical breakdown of the research layer, C++ live runtime, risk authority, Redis/Postgres design, adaptive execution and current improvement roadmap.

## Current Direction

I am optimizing for quant developer and research engineering roles where the work needs both market understanding and production-quality systems thinking: building models, testing them, wiring them into risk-aware execution, and knowing exactly where research ends and live trading begins.
