from __future__ import annotations

import unittest

from hyperview.models import BacktestMetrics
from hyperview.pine.exporter import (
    build_metric_filename,
    inject_default_inputs,
    resolve_optimization_report_dir,
)
from hyperview.pine.optimizer import PineCandidate


class PineExporterTests(unittest.TestCase):
    def test_build_metric_filename_compact_template(self) -> None:
        candidate = _candidate(
            pair="OANDA:XAUUSD",
            timeframe="15m",
            net_profit_pct=46.8,
            max_drawdown_pct=8.66,
            profit_factor=2.03,
            trade_count=158,
        )
        name = build_metric_filename(
            template="{symbol}_{tf}_{strategy}_np{net}_dd{dd}_pf{pf}_tc{trades}.pine",
            pair=candidate.pair,
            timeframe=candidate.timeframe,
            strategy_name="drsi",
            candidate=candidate,
        )
        self.assertEqual(name, "xauusd_m15_drsi_np46.80_dd8.66_pf2.03_tc158.pine")

    def test_inject_default_inputs_overrides_only_present_input_lines(self) -> None:
        source = """
entryMode = input.string("both", "Entry Mode", options=["both", "aggressive"])
confirmBars = input.int(24, "Confirm Bars", minval=3)
plot(close)
""".strip()
        updated, touched = inject_default_inputs(
            source,
            {
                "entryMode": "aggressive",
                "confirmBars": 12,
                "unknownKey": 99,
            },
        )
        self.assertEqual(touched, 2)
        self.assertIn('entryMode = input.string("aggressive"', updated)
        self.assertIn("confirmBars = input.int(12,", updated)
        self.assertNotIn("unknownKey", updated)

    def test_resolve_optimization_report_dir_uses_symbol_and_timeframe(self) -> None:
        path = resolve_optimization_report_dir(
            output_dir="results",
            pair="OANDA:XAUUSD",
            timeframe="15m",
            explicit_report_dir=None,
        )
        self.assertEqual(str(path).replace("\\", "/"), "results/optimizations/xauusd/15m")


def _candidate(
    *,
    pair: str,
    timeframe: str,
    net_profit_pct: float,
    max_drawdown_pct: float,
    profit_factor: float,
    trade_count: int,
) -> PineCandidate:
    return PineCandidate(
        pair=pair,
        timeframe=timeframe,
        params={},
        settings={},
        metrics=BacktestMetrics(
            symbol=pair,
            timeframe=timeframe,
            start=None,
            end=None,
            mode="long",
            sl_pct=1.0,
            tp_pct=2.0,
            net_profit_pct=net_profit_pct,
            max_drawdown_pct=max_drawdown_pct,
            win_rate_pct=50.0,
            profit_factor=profit_factor,
            trade_count=trade_count,
            equity_final=100_000.0,
        ),
        trades=[],
        map_id="1h_15m",
        session_window="0700-1700|1200-2200",
        analysis_tags=[],
    )


if __name__ == "__main__":
    unittest.main()
