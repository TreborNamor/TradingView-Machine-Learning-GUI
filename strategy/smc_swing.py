from __future__ import annotations

from typing import Any

import pandas as pd

from . import register_strategy
from .base import BaseStrategy
from .smc_core import generate_smc_frame


@register_strategy
class SmcSwingStrategy(BaseStrategy):
    """HTF sweep -> LTF CHoCH -> OB entry strategy with dynamic SL/TP."""

    strategy_name = "smc_swing"

    def default_settings(self) -> dict[str, Any]:
        return {
            "htf_timeframe": "1h",
            "ltf_timeframe": "5m",
            "map_id": "1h_5m",
            "entry_mode": "both",  # retest_ob | aggressive | both
            "htf_swing_lookback": 6,
            "choch_lookback": 8,
            "confirm_window_bars": 24,
            "ob_lookback_bars": 20,
            "retest_window_bars": 12,
            "atr_length": 14,
            "sl_buffer_atr": 0.25,
            "rr_target": 2.0,
            "min_risk_atr": 0.15,
            "max_chase_atr": 2.0,
            "session_filter_enabled": True,
            "session_windows_utc": [[7, 17], [12, 22]],
            "enable_long": True,
            "enable_short": True,
            "start": None,
            "end": None,
        }

    def required_columns(self) -> list[str]:
        return ["time", "open", "high", "low", "close"]

    def generate_signals(self, candles: pd.DataFrame, settings: dict[str, Any]) -> pd.DataFrame:
        s = {**self.default_settings(), **settings}
        dataframe = self.prepare_candles(candles)
        dataframe = generate_smc_frame(dataframe, s)
        self._apply_date_range(dataframe, s["start"], s["end"])

        dataframe["buy_signal"] = dataframe["buy_signal"] & dataframe["in_date_range"]
        dataframe["sell_signal"] = dataframe["sell_signal"] & dataframe["in_date_range"]
        dataframe["enable_long"] = bool(s["enable_long"])
        dataframe["enable_short"] = bool(s["enable_short"])
        return dataframe
