#!/usr/bin/env python3
"""Run the public modular Python research-system showcase."""

from __future__ import annotations

from market_data import generate_market_slices
from replay import run_replay
from reports import build_report, to_pretty_json
from validation import walk_forward


def main() -> None:
    slices = generate_market_slices(length=260, seed=17)
    validation = walk_forward(slices)
    threshold = validation["windows"][-1]["threshold"] if validation["windows"] else 0.0035
    replay = run_replay(slices, threshold=threshold)
    print(to_pretty_json(build_report(replay, validation)))


if __name__ == "__main__":
    main()
