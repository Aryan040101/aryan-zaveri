# Evidence Policy

This repository is designed to show engineering and research capability without exposing confidential trading logic or sensitive operational data.

## Evidence Categories

### Research

Hypotheses, feature studies, strategy families, market relationships, model ideas and reports. Research artifacts can be useful without being production-ready.

### Simulation

Backtests and walk-forward studies using historical data. Simulation results are labeled as simulation and are not presented as audited live trading performance.

### Replay

Systems that replay historical or live-current signals through risk, execution and PnL accounting logic. Replay is useful for testing behavior, assumptions and instrumentation.

### Paper / Live System Activity

Evidence that live components produced signals, risk decisions, order intents, journals or paper/live workflow outputs. This is system-activity evidence, not the same as audited profitability.

### Audited Live Performance

Broker/exchange-reconciled, independently reviewable live PnL and position evidence. This repository does not claim audited live performance.

## What Is Safe To Show

- High-level architecture.
- Sanitized case studies.
- Aggregate counts and metric categories.
- Public-safe descriptions of research areas.
- Evidence boundaries and lessons learned.

## What Is Not Shown

- API keys, passwords or credentials.
- Raw order IDs or account identifiers.
- Broker secrets or private customer data.
- Proprietary alpha rules, thresholds or exact strategy logic.
- Employer-sensitive implementation details.
- Raw logs, private databases or data dumps.

## Public Claim Standard

Every claim should be defensible in an interview. If a result is from simulation, replay or paper/live activity, it is labeled that way. If something has not been independently audited, it is not described as audited performance.

