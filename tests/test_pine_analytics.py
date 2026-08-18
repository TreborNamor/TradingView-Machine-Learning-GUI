from __future__ import annotations

import unittest
import sys
import types

sys.modules.setdefault("talib", types.ModuleType("talib"))

from hyperview.models import BacktestMetrics, Trade
from hyperview.pine.analytics import analyze_best_when
from hyperview.pine.optimizer import PineCandidate

class PineAnalyticsTests(unittest.TestCase):
    def test_best_when_grouping_and_gate(self) -> None:
        metrics = BacktestMetrics(
            symbol="OANDA:EURUSD",
            timeframe="5m",
            start=None,
            end=None,
            mode="long",
            sl_pct=1.0,
            tp_pct=2.0,
            net_profit_pct=10.0,
            max_drawdown_pct=3.0,
            win_rate_pct=50.0,
            profit_factor=1.2,
            trade_count=4,
            equity_final=110000.0,
        )
        trades = [
            Trade(1714521600, 1714525200, "long", 1.0, 1.01, "take_profit", 1.0, 100000.0, 101000.0),  # 2024-05-01 01:00 UTC
            Trade(1714528800, 1714532400, "long", 1.0, 1.02, "take_profit", 2.0, 101000.0, 103020.0),  # 03:00 UTC
            Trade(1714572000, 1714575600, "long", 1.0, 0.99, "stop_loss", -1.0, 103020.0, 101989.8),   # 15:00 UTC
            Trade(1714579200, 1714582800, "long", 1.0, 1.03, "take_profit", 3.0, 101989.8, 105049.49), # 17:00 UTC
        ]
        candidate = PineCandidate(
            pair="OANDA:EURUSD",
            timeframe="5m",
            params={},
            settings={},
            metrics=metrics,
            trades=trades,
            map_id="1h_5m",
            session_window="0700-1700|1200-2200",
            analysis_tags=[],
        )
        analysis = analyze_best_when([candidate], min_trades=1)
        self.assertTrue(len(analysis["best_by_session_hour"]) >= 1)
        self.assertTrue(len(analysis["best_by_month_quarter"]) >= 1)
        self.assertTrue(len(analysis["best_by_map_hour"]) >= 1)
        strict = analyze_best_when([candidate], min_trades=10)
        self.assertEqual(strict["best_by_session_hour"], [])

if __name__ == "__main__":
    unittest.main()
