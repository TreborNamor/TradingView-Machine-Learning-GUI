from __future__ import annotations

import unittest
import sys
import types

sys.modules.setdefault("talib", types.ModuleType("talib"))

from hyperview.models import BacktestMetrics
from hyperview.pine.inputs import SearchDimension
from hyperview.pine.optimizer import PineCandidate, run_two_stage_optimization

class PineOptimizerTests(unittest.TestCase):
    def test_two_stage_returns_ranked_candidates(self) -> None:
        dimensions = [
            SearchDimension(
                name="entryMode",
                dim_type="categorical",
                strategy_key="entry_mode",
                impacts_pnl=True,
                default="both",
                values=["retest_ob", "aggressive", "both"],
            ),
            SearchDimension(
                name="confirmBars",
                dim_type="int",
                strategy_key="confirm_window_bars",
                impacts_pnl=True,
                default=24,
                minval=5,
                maxval=30,
                step=1,
            ),
        ]

        def _evaluate(params, *, min_trades, min_signals):
            metric = BacktestMetrics(
                symbol="X:Y",
                timeframe="5m",
                start=None,
                end=None,
                mode="long",
                sl_pct=1.0,
                tp_pct=2.0,
                net_profit_pct=float(params["confirmBars"]),
                max_drawdown_pct=5.0,
                win_rate_pct=50.0,
                profit_factor=1.0,
                trade_count=max(min_trades, 10),
                equity_final=100000.0 + float(params["confirmBars"]),
            )
            return PineCandidate(
                pair="X:Y",
                timeframe="5m",
                params=dict(params),
                settings={},
                metrics=metric,
                trades=[],
                map_id="1h_5m",
                session_window="0700-1700|1200-2200",
                analysis_tags=[],
            )

        ranked = run_two_stage_optimization(
            dimensions=dimensions,
            objective="net_profit_pct",
            coarse_trials=5,
            fine_trials=10,
            coarse_top_k=2,
            min_trades=5,
            min_signals=5,
            fine_span_ratio=0.3,
            time_budget_seconds=20,
            watchdog_seconds=1,
            evaluate_candidate=_evaluate,
        )
        self.assertTrue(len(ranked) >= 1)
        self.assertGreaterEqual(ranked[0].metrics.net_profit_pct, ranked[-1].metrics.net_profit_pct)

if __name__ == "__main__":
    unittest.main()
