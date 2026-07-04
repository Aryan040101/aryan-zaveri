"""Report assembly for the public Python research-system showcase."""

from __future__ import annotations

import json


def build_report(replay: dict, validation: dict) -> dict:
    return {
        "demo": "python_research_system",
        "version": "public.v1",
        "research_stack": [
            "market_data",
            "features",
            "signals",
            "walk_forward_validation",
            "risk",
            "portfolio",
            "execution",
            "replay",
            "reports",
        ],
        "replay_summary": replay["summary"],
        "portfolio_state": replay["portfolio_state"],
        "validation_summary": validation["summary"],
        "validation_windows": validation["windows"],
        "events_sample": replay["events"][:18],
    }


def to_pretty_json(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True)
