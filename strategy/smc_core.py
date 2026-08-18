from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from .indicators import atr, barssince


@dataclass(frozen=True)
class SmcMap:
    htf: str
    ltf: str
    map_id: str


def _timeframe_seconds(value: str) -> int:
    text = value.strip().lower()
    unit = text[-1]
    amount = int(text[:-1]) if text[:-1].isdigit() else 1
    if unit == "m":
        return amount * 60
    if unit == "h":
        return amount * 3600
    if unit == "d":
        return amount * 86400
    if unit == "w":
        return amount * 604800
    if text == "1mo":
        return 30 * 86400
    raise ValueError(f"Unsupported timeframe: {value}")


def _derive_htf_lookback(base_lookback: int, ltf: str, htf: str) -> int:
    ltf_seconds = _timeframe_seconds(ltf)
    htf_seconds = _timeframe_seconds(htf)
    ratio = max(1, int(round(htf_seconds / max(ltf_seconds, 1))))
    return max(base_lookback * ratio, base_lookback + 1)


def _build_session_mask(
    timestamps: pd.Series,
    *,
    enabled: bool,
    windows_utc: list[list[int]] | None,
) -> pd.Series:
    if not enabled:
        return pd.Series(True, index=timestamps.index)
    windows = windows_utc or [[7, 17], [12, 22]]
    hours = pd.to_datetime(timestamps, unit="s", utc=True).dt.hour
    mask = pd.Series(False, index=timestamps.index)
    for item in windows:
        if len(item) != 2:
            continue
        start, end = int(item[0]), int(item[1])
        if start == end:
            mask = mask | True
        elif start < end:
            mask = mask | ((hours >= start) & (hours < end))
        else:
            # Supports overnight windows.
            mask = mask | ((hours >= start) | (hours < end))
    return mask


def _last_index_where(series: pd.Series, start: int, end: int, target: bool = True) -> int | None:
    for idx in range(end, start - 1, -1):
        if bool(series.iloc[idx]) is target:
            return idx
    return None


def _populate_retest_signals(
    dataframe: pd.DataFrame,
    *,
    long_confirm_col: str,
    short_confirm_col: str,
    ob_high_col: str,
    ob_low_col: str,
    retest_bars: int,
) -> tuple[pd.Series, pd.Series]:
    buy = pd.Series(False, index=dataframe.index)
    sell = pd.Series(False, index=dataframe.index)

    pending_long: dict[str, float | int] | None = None
    pending_short: dict[str, float | int] | None = None

    for i in range(len(dataframe)):
        if bool(dataframe.at[i, long_confirm_col]):
            pending_long = {
                "expires": i + retest_bars,
                "ob_low": float(dataframe.at[i, ob_low_col]),
                "ob_high": float(dataframe.at[i, ob_high_col]),
            }
        if bool(dataframe.at[i, short_confirm_col]):
            pending_short = {
                "expires": i + retest_bars,
                "ob_low": float(dataframe.at[i, ob_low_col]),
                "ob_high": float(dataframe.at[i, ob_high_col]),
            }

        low = float(dataframe.at[i, "low"])
        high = float(dataframe.at[i, "high"])

        if pending_long is not None:
            if i > int(pending_long["expires"]):
                pending_long = None
            else:
                ob_low = float(pending_long["ob_low"])
                ob_high = float(pending_long["ob_high"])
                if low <= ob_high and high >= ob_low:
                    buy.iloc[i] = True
                    pending_long = None

        if pending_short is not None:
            if i > int(pending_short["expires"]):
                pending_short = None
            else:
                ob_low = float(pending_short["ob_low"])
                ob_high = float(pending_short["ob_high"])
                if high >= ob_low and low <= ob_high:
                    sell.iloc[i] = True
                    pending_short = None

    return buy, sell


def generate_smc_frame(candles: pd.DataFrame, settings: dict[str, Any]) -> pd.DataFrame:
    dataframe = candles.copy()
    dataframe = dataframe.reset_index(drop=True)
    dataframe["atr"] = atr(dataframe["high"], dataframe["low"], dataframe["close"], int(settings["atr_length"]))

    htf_lookback = _derive_htf_lookback(
        int(settings["htf_swing_lookback"]),
        str(settings["ltf_timeframe"]),
        str(settings["htf_timeframe"]),
    )
    choch_lookback = max(2, int(settings["choch_lookback"]))
    confirm_window = max(1, int(settings["confirm_window_bars"]))
    ob_lookback = max(2, int(settings["ob_lookback_bars"]))

    dataframe["htf_swing_high"] = dataframe["high"].shift(1).rolling(htf_lookback, min_periods=htf_lookback).max()
    dataframe["htf_swing_low"] = dataframe["low"].shift(1).rolling(htf_lookback, min_periods=htf_lookback).min()

    dataframe["bull_sweep"] = (
        (dataframe["low"] < dataframe["htf_swing_low"]) & (dataframe["close"] > dataframe["htf_swing_low"])
    )
    dataframe["bear_sweep"] = (
        (dataframe["high"] > dataframe["htf_swing_high"]) & (dataframe["close"] < dataframe["htf_swing_high"])
    )
    dataframe["bars_since_bull_sweep"] = barssince(dataframe["bull_sweep"]).fillna(1_000_000)
    dataframe["bars_since_bear_sweep"] = barssince(dataframe["bear_sweep"]).fillna(1_000_000)

    micro_high = dataframe["high"].shift(1).rolling(choch_lookback, min_periods=choch_lookback).max()
    micro_low = dataframe["low"].shift(1).rolling(choch_lookback, min_periods=choch_lookback).min()
    dataframe["bull_choch"] = dataframe["close"] > micro_high
    dataframe["bear_choch"] = dataframe["close"] < micro_low

    dataframe["bull_confirm"] = (
        (dataframe["bars_since_bull_sweep"] <= confirm_window) & dataframe["bull_choch"]
    )
    dataframe["bear_confirm"] = (
        (dataframe["bars_since_bear_sweep"] <= confirm_window) & dataframe["bear_choch"]
    )

    dataframe["sweep_low_anchor"] = np.where(dataframe["bull_sweep"], dataframe["low"], np.nan)
    dataframe["sweep_low_anchor"] = pd.Series(dataframe["sweep_low_anchor"]).ffill().to_numpy()
    dataframe["sweep_high_anchor"] = np.where(dataframe["bear_sweep"], dataframe["high"], np.nan)
    dataframe["sweep_high_anchor"] = pd.Series(dataframe["sweep_high_anchor"]).ffill().to_numpy()

    dataframe["ob_low"] = np.nan
    dataframe["ob_high"] = np.nan
    bearish_candle = dataframe["close"] < dataframe["open"]
    bullish_candle = dataframe["close"] > dataframe["open"]

    for i in range(len(dataframe)):
        if bool(dataframe.at[i, "bull_confirm"]):
            j = _last_index_where(bearish_candle, max(0, i - ob_lookback), i - 1, target=True)
            if j is not None:
                dataframe.at[i, "ob_low"] = float(dataframe.at[j, "low"])
                dataframe.at[i, "ob_high"] = float(dataframe.at[j, "high"])
        if bool(dataframe.at[i, "bear_confirm"]):
            j = _last_index_where(bullish_candle, max(0, i - ob_lookback), i - 1, target=True)
            if j is not None:
                dataframe.at[i, "ob_low"] = float(dataframe.at[j, "low"])
                dataframe.at[i, "ob_high"] = float(dataframe.at[j, "high"])

    dataframe["ob_low"] = dataframe["ob_low"].ffill()
    dataframe["ob_high"] = dataframe["ob_high"].ffill()

    entry_mode = str(settings["entry_mode"]).lower()
    if entry_mode not in {"retest_ob", "aggressive", "both"}:
        raise ValueError(f"Unsupported entry_mode: {entry_mode}")

    aggressive_buy = dataframe["bull_confirm"].copy()
    aggressive_sell = dataframe["bear_confirm"].copy()
    retest_buy, retest_sell = _populate_retest_signals(
        dataframe,
        long_confirm_col="bull_confirm",
        short_confirm_col="bear_confirm",
        ob_high_col="ob_high",
        ob_low_col="ob_low",
        retest_bars=max(1, int(settings["retest_window_bars"])),
    )

    if entry_mode == "aggressive":
        dataframe["buy_signal_raw"] = aggressive_buy
        dataframe["sell_signal_raw"] = aggressive_sell
    elif entry_mode == "retest_ob":
        dataframe["buy_signal_raw"] = retest_buy
        dataframe["sell_signal_raw"] = retest_sell
    else:
        dataframe["buy_signal_raw"] = aggressive_buy | retest_buy
        dataframe["sell_signal_raw"] = aggressive_sell | retest_sell

    session_mask = _build_session_mask(
        dataframe["time"],
        enabled=bool(settings["session_filter_enabled"]),
        windows_utc=settings.get("session_windows_utc"),
    )
    dataframe["session_allowed"] = session_mask

    sl_buffer = float(settings["sl_buffer_atr"])
    rr_target = float(settings["rr_target"])
    min_risk_atr = float(settings["min_risk_atr"])
    max_chase_atr = float(settings["max_chase_atr"])

    dataframe["dynamic_stop_price"] = np.nan
    dataframe["dynamic_target_price"] = np.nan
    dataframe["buy_signal"] = False
    dataframe["sell_signal"] = False
    dataframe["entry_mode"] = entry_mode
    dataframe["map_id"] = str(settings["map_id"])

    for i in range(len(dataframe)):
        close_price = float(dataframe.at[i, "close"])
        atr_value = float(dataframe.at[i, "atr"]) if pd.notna(dataframe.at[i, "atr"]) else np.nan
        if not np.isfinite(atr_value) or atr_value <= 0:
            continue

        if bool(dataframe.at[i, "buy_signal_raw"]) and bool(dataframe.at[i, "session_allowed"]):
            sweep_low = float(dataframe.at[i, "sweep_low_anchor"])
            ob_mid = (float(dataframe.at[i, "ob_low"]) + float(dataframe.at[i, "ob_high"])) / 2.0
            if np.isfinite(ob_mid) and abs(close_price - ob_mid) <= atr_value * max_chase_atr:
                stop = sweep_low - atr_value * sl_buffer
                risk = close_price - stop
                if risk >= atr_value * min_risk_atr:
                    target = close_price + risk * rr_target
                    dataframe.at[i, "dynamic_stop_price"] = stop
                    dataframe.at[i, "dynamic_target_price"] = target
                    dataframe.at[i, "buy_signal"] = True

        if bool(dataframe.at[i, "sell_signal_raw"]) and bool(dataframe.at[i, "session_allowed"]):
            sweep_high = float(dataframe.at[i, "sweep_high_anchor"])
            ob_mid = (float(dataframe.at[i, "ob_low"]) + float(dataframe.at[i, "ob_high"])) / 2.0
            if np.isfinite(ob_mid) and abs(close_price - ob_mid) <= atr_value * max_chase_atr:
                stop = sweep_high + atr_value * sl_buffer
                risk = stop - close_price
                if risk >= atr_value * min_risk_atr:
                    target = close_price - risk * rr_target
                    dataframe.at[i, "dynamic_stop_price"] = stop
                    dataframe.at[i, "dynamic_target_price"] = target
                    dataframe.at[i, "sell_signal"] = True

    dataframe["sweep_detected"] = dataframe["bull_sweep"] | dataframe["bear_sweep"]
    dataframe["choch_confirmed"] = dataframe["bull_confirm"] | dataframe["bear_confirm"]
    dataframe["ob_touched"] = retest_buy | retest_sell
    return dataframe
