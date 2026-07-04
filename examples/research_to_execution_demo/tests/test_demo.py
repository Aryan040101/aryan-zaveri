from __future__ import annotations

from pathlib import Path
import sys
import unittest


DEMO_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEMO_DIR))

from execution import OrderIntent, simulate_fill
from features import build_features
from market import GLOBAL, OIL, TARGET, MarketFrame, generate_market
from replay import run_replay
from risk import RiskLimits, evaluate_signal
from signals import Signal


class DemoTests(unittest.TestCase):
    def test_replay_summary_is_deterministic(self) -> None:
        result = run_replay(generate_market(length=180, seed=7))
        self.assertEqual(
            result["summary"],
            {
                "accepted_intents": 22,
                "evidence_type": "synthetic_demo",
                "fees": 140.9626,
                "final_equity": 99568.8445,
                "gross_pnl": -219.836,
                "max_drawdown": -0.0117,
                "net_pnl": -360.7986,
                "not_claimed": "real alpha or live performance",
                "rejected_intents": 84,
                "slippage_cost": 105.7219,
                "trades": 22,
                "win_rate": 0.4545,
            },
        )

    def test_features_do_not_change_when_future_prices_change(self) -> None:
        frames = generate_market(length=60, seed=11)
        index = 25
        baseline = build_features(frames, index)

        modified = list(frames)
        for j in range(index + 1, len(modified)):
            frame = modified[j]
            modified[j] = MarketFrame(
                t=frame.t,
                prices={
                    TARGET: frame.prices[TARGET] * 5.0,
                    GLOBAL: frame.prices[GLOBAL] * 0.2,
                    OIL: frame.prices[OIL] * 3.0,
                },
                volumes=frame.volumes,
            )

        self.assertEqual(baseline, build_features(modified, index))

    def test_risk_rejects_duplicate_position_and_drawdown_pause(self) -> None:
        class State:
            equity = 100_000.0
            current_drawdown = 0.0
            position = object()

        signal = Signal(t=1, symbol=TARGET, score=0.01, direction=1, reason="test")
        duplicate = evaluate_signal(signal, State(), 100.0, RiskLimits())
        self.assertFalse(duplicate.accepted)
        self.assertEqual(duplicate.reason, "duplicate_position")

        class DrawdownState:
            equity = 100_000.0
            current_drawdown = -0.10
            position = None

        paused = evaluate_signal(signal, DrawdownState(), 100.0, RiskLimits(max_drawdown=0.05))
        self.assertFalse(paused.accepted)
        self.assertEqual(paused.reason, "drawdown_pause")

    def test_fill_model_accounts_for_fee_and_slippage(self) -> None:
        intent = OrderIntent(
            t=10,
            symbol=TARGET,
            action="OPEN",
            side=1,
            quantity=100,
            reference_price=100.0,
            reason="test",
        )
        fill = simulate_fill(intent, market_price=100.0, fee_bps=2.0, slippage_bps=1.5)
        self.assertEqual(fill.fill_price, 100.015)
        self.assertEqual(fill.fee, 2.0003)
        self.assertEqual(fill.slippage_cost, 1.5)

    def test_replay_result_shape_is_public_safe(self) -> None:
        result = run_replay(generate_market(length=80, seed=3))
        self.assertIn("summary", result)
        self.assertIn("trades", result)
        self.assertEqual(result["summary"]["evidence_type"], "synthetic_demo")
        self.assertEqual(result["summary"]["not_claimed"], "real alpha or live performance")
        self.assertIsInstance(result["trades"], list)


if __name__ == "__main__":
    unittest.main()

