# Aryan Zaveri

**Quant Developer | Trading Systems | Research Infrastructure | Execution-Aware Systems**

[LinkedIn](https://www.linkedin.com/in/aryan-zaveri0401/) · [Public CV](resume/Aryan_Zaveri_Quant_Developer.pdf)

I build trading systems from the ground up: market data, feature engineering, strategy research, backtests, risk checks, order intent generation, execution tracking, replay, and post-trade analysis.

My strongest work is end-to-end quant infrastructure. I use Python mainly for research, backtesting, analytics and reports. I use C++ for live/runtime systems where latency, memory use, sockets, queues, order state and risk authority matter. The systems communicate through JSON contracts, keep hot state in Redis, and persist historical/research state into PostgreSQL or Timescale-style stores.

## What I Build

- **Research and backtesting:** factor studies, feature pipelines, walk-forward tests, replay engines, simulation reports and metric extraction.
- **Live trading runtime:** C++ sockets, order managers, risk managers, working-order state, execution journals, heartbeats and recovery loops.
- **Risk authority:** one independent risk layer that controls global capital, segment capital, side limits, symbol limits, active order limits and hard exits.
- **Adaptive execution:** quote freshness checks, spread/slippage gates, price leaning, replace/adjust loops, chunking, ladder exits and position-aware adjustments.
- **Cross-market research:** linking Indian markets with global indices, crude oil, FX, macro data, sector themes, options/futures behavior and crypto risk appetite.
- **Storage and state:** Redis for hot state and queues; PostgreSQL for durable candles, instruments, Greeks, analytics, snapshots and research outputs.

This public repo uses sanitized descriptions and synthetic examples. It is meant to show architecture and engineering taste, not publish private strategy rules.

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

## Flagship Work: Vajra

**Vajra** is my personal multi-asset research and trading infrastructure platform. It is not a company.

The goal behind Vajra is to avoid looking at one instrument in isolation. A model should be able to reason across seconds, minutes, hours, days, weeks and months. It should connect Indian sectors with oil, global markets, US/China/Japan/Korea sector behavior, domestic macro, global macro, volatility, options/futures structure and broader risk appetite.

The work is about quantifying relationships, testing whether they survive history, simulating them under realistic costs, and then connecting the surviving ideas to risk and execution systems. That includes buying weakness, selling strength, finding themes, tracking cross-asset confirmation, and turning those views into rules that can be backtested, replayed and implemented.

The public version focuses on the engineering shape:

- Python research, feature engineering and backtesting.
- C++ live sockets, `socket.cpp` / `risk.cpp` style components, order managers and execution runtimes.
- JSON contracts between research, risk, execution and journals.
- Redis streams, queues, hashes and heartbeats for hot state.
- PostgreSQL writers for instruments, candles, Greeks, snapshots and reports.
- Single risk authority for capital, segment, side, symbol and active-order controls.

## Professional Experience

### GreyOak Capital — Quantitative Developer

I work on quantitative research systems, market-intelligence infrastructure and research-facing tooling. Public-safe areas include Horizon, Compass, Context-Intelligence and Ask-GreyOak: systems that bring market context, internal data flows, dashboards, WebSocket/data contracts and analyst-facing interfaces together.

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
