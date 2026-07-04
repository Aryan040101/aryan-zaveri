#!/usr/bin/env python3
"""Run the sanitized public research-to-execution demo."""

from __future__ import annotations

import json

from market import generate_market
from replay import run_replay


def main() -> None:
    frames = generate_market(length=180, seed=7)
    result = run_replay(frames)
    print(json.dumps(result["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

