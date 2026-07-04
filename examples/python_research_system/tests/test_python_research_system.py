from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


SYSTEM_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SYSTEM_DIR))

from features import build_feature_row
from market_data import SYMBOLS, MarketSlice, generate_market_slices
from replay import run_replay
from risk import RiskLimits, evaluate
from signals import Signal
from validation import choose_threshold, walk_forward


class PythonResearchSystemTests(unittest.TestCase):
    def test_features_do_not_use_future_slices(self) -> None:
        slices = generate_market_slices(length=80, seed=21)
        index = 35
        baseline = build_feature_row(slices, index)
        modified = list(slices)
        for pos in range(index + 1, len(modified)):
            current = modified[pos]
            modified[pos] = MarketSlice(
                t=current.t,
                closes={symbol: value * 3.0 for symbol, value in current.closes.items()},
                volumes={symbol: value * 5 for symbol, value in current.volumes.items()},
            )
        self.assertEqual(baseline, build_feature_row(modified, index))

    def test_threshold_selection_is_from_known_grid(self) -> None:
        slices = generate_market_slices(length=130, seed=2)
        rows = [build_feature_row(slices, idx) for idx in range(24, 110)]
        self.assertIn(choose_threshold(rows), {0.0025, 0.0035, 0.0045, 0.0055})

    def test_risk_rejects_duplicate_position(self) -> None:
        class State:
            equity = 100_000.0
            current_drawdown = 0.0
            positions = {SYMBOLS["target"]: object()}

        decision = evaluate(
            Signal(1, SYMBOLS["target"], 1, 0.01, 0.8, "test"),
            State(),
            100.0,
            RiskLimits(),
        )
        self.assertFalse(decision.accepted)
        self.assertEqual(decision.reason, "active_position_limit")

    def test_replay_contains_lifecycle_events(self) -> None:
        result = run_replay(generate_market_slices(length=150, seed=9), threshold=0.0035)
        self.assertEqual(result["summary"]["evidence_type"], "synthetic_research_system")
        event_names = {event["event"] for event in result["events"]}
        self.assertIn("signal_generated", event_names)
        self.assertIn("risk_decision", event_names)
        self.assertIn("order_intent", event_names)
        self.assertIn("execution_fill", event_names)
        self.assertIn("equity", result["portfolio_state"])

    def test_walk_forward_summary_shape(self) -> None:
        result = walk_forward(generate_market_slices(length=220, seed=17), train=70, test=35)
        self.assertGreaterEqual(result["summary"]["windows"], 2)
        self.assertEqual(result["summary"]["validation"], "walk_forward_synthetic")
        self.assertTrue(all("threshold" in window for window in result["windows"]))

    def test_entrypoint_emits_json_report(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(SYSTEM_DIR / "run_system.py")],
            cwd=SYSTEM_DIR,
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertIn('"demo": "python_research_system"', proc.stdout)
        self.assertIn('"research_stack"', proc.stdout)


if __name__ == "__main__":
    unittest.main()
