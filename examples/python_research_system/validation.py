"""Walk-forward threshold validation for the public Python research system."""

from __future__ import annotations

from features import build_feature_table
from market_data import MarketSlice
from replay import run_replay
from signals import score_row


THRESHOLDS = [0.0025, 0.0035, 0.0045, 0.0055]


def choose_threshold(feature_rows: list[dict[str, float]]) -> float:
    """Select a threshold using only training rows."""

    best_threshold = THRESHOLDS[0]
    best_score = -1.0
    for threshold in THRESHOLDS:
        actionable = 0
        correct_direction = 0
        for idx, row in enumerate(feature_rows[:-1]):
            score = score_row(row)
            if abs(score) <= threshold:
                continue
            actionable += 1
            next_ret = feature_rows[idx + 1]["target_ret_1"]
            if (score > 0 and next_ret > 0) or (score < 0 and next_ret < 0):
                correct_direction += 1
        hit_rate = correct_direction / actionable if actionable else 0.0
        objective = hit_rate * min(actionable, 40) / 40.0
        if objective > best_score:
            best_score = objective
            best_threshold = threshold
    return best_threshold


def walk_forward(slices: list[MarketSlice], train: int = 90, test: int = 45, start_index: int = 24) -> dict:
    windows: list[dict] = []
    cursor = start_index + train
    while cursor + test < len(slices) - 1:
        train_rows = build_feature_table(slices[:cursor], start_index=start_index)
        threshold = choose_threshold(train_rows)
        replay = run_replay(slices, threshold=threshold, start_index=cursor, end_index=cursor + test)
        windows.append(
            {
                "train_end": cursor,
                "test_end": cursor + test,
                "threshold": threshold,
                "summary": replay["summary"],
            }
        )
        cursor += test

    total_trades = sum(window["summary"]["trades"] for window in windows)
    total_net = sum(window["summary"]["net_pnl"] for window in windows)
    return {
        "windows": windows,
        "summary": {
            "windows": len(windows),
            "total_trades": total_trades,
            "total_net_pnl": round(total_net, 4),
            "validation": "walk_forward_synthetic",
        },
    }
