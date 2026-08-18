from __future__ import annotations

import math
from dataclasses import dataclass
from typing import NamedTuple

import numpy as np
import pandas as pd

from ..models import BacktestMetrics, BacktestResult, CandleRequest, Mode, RiskParameters, Trade

# Approximate number of bars per year for Sharpe annualization.
_BARS_PER_YEAR: dict[str, float] = {
    "1":    365 * 24 * 60,   # 1m
    "3":    365 * 24 * 20,   # 3m
    "5":    365 * 24 * 12,   # 5m
    "15":   365 * 24 * 4,    # 15m
    "30":   365 * 24 * 2,    # 30m
    "45":   365 * 16,        # 45m
    "60":   365 * 24,        # 1h
    "120":  365 * 12,        # 2h
    "180":  365 * 8,         # 3h
    "240":  365 * 6,         # 4h
    "1D":   365,
    "1W":   52,
    "1M":   12,
}


def _annualization_factor(timeframe: str) -> float:
    """Return sqrt(bars-per-year) for Sharpe annualization."""
    # Normalize aliases: "1h" → "60", "4h" → "240"; raw strings pass through.
    tf = timeframe.upper().replace(" ", "")
    if tf.endswith("H"):
        try:
            tf = str(int(tf[:-1]) * 60)
        except ValueError:
            pass
    return math.sqrt(_BARS_PER_YEAR.get(tf, 365 * 24))  # default to 1h


class _Position(NamedTuple):
    direction: str
    entry_time: int
    entry_price: float
    stop_price: float
    target_price: float
    equity_before: float


class _PendingOrder(NamedTuple):
    action: str
    signal_close: float
    dynamic_stop_price: float | None = None
    dynamic_target_price: float | None = None


class _CompiledSignalFrame(NamedTuple):
    time: list[int]
    open: list[float]
    high: list[float]
    low: list[float]
    close: list[float]
    in_date_range: list[bool]
    buy_signal: list[bool]
    sell_signal: list[bool]
    enable_long: list[bool]
    enable_short: list[bool]
    dynamic_stop_price: list[float | None]
    dynamic_target_price: list[float | None]
    end_date: str | None
    length: int


@dataclass
class _MetricsAccumulator:
    initial_equity: float
    final_closed_equity: float
    positive_pnl: float = 0.0
    negative_pnl: float = 0.0
    wins: int = 0
    trade_count: int = 0
    win_return_sum: float = 0.0
    win_return_count: int = 0
    loss_return_sum: float = 0.0
    loss_return_count: int = 0
    total_return_sum: float = 0.0
    worst_trade: float = float("inf")
    max_consec_losses: int = 0
    current_consec_losses: int = 0
    sl_exits: int = 0
    tp_exits: int = 0
    peak_equity: float = 0.0
    max_drawdown: float = 0.0
    prev_curve_value: float = 0.0
    return_count: int = 0
    return_mean: float = 0.0
    return_m2: float = 0.0

    @classmethod
    def create(cls, initial_equity: float) -> _MetricsAccumulator:
        return cls(
            initial_equity=initial_equity,
            final_closed_equity=initial_equity,
            peak_equity=initial_equity,
            prev_curve_value=initial_equity,
        )

    def record_trade(self, trade: Trade) -> None:
        pnl = trade.equity_after - self.final_closed_equity
        self.final_closed_equity = trade.equity_after
        self.trade_count += 1
        self.total_return_sum += trade.return_pct
        self.worst_trade = min(self.worst_trade, trade.return_pct)

        if pnl >= 0:
            self.positive_pnl += pnl
            self.wins += 1
            self.win_return_sum += trade.return_pct
            self.win_return_count += 1
            self.current_consec_losses = 0
        else:
            self.negative_pnl += pnl
            self.loss_return_sum += trade.return_pct
            self.loss_return_count += 1
            self.current_consec_losses += 1
            self.max_consec_losses = max(self.max_consec_losses, self.current_consec_losses)

        if trade.exit_reason == "stop_loss":
            self.sl_exits += 1
        elif trade.exit_reason == "take_profit":
            self.tp_exits += 1

    def observe_equity(self, curve_value: float) -> None:
        if curve_value > self.peak_equity:
            self.peak_equity = curve_value
        if self.peak_equity > 0:
            drawdown = ((self.peak_equity - curve_value) / self.peak_equity) * 100.0
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown

        if self.prev_curve_value != 0:
            bar_return = (curve_value - self.prev_curve_value) / self.prev_curve_value
            self.return_count += 1
            delta = bar_return - self.return_mean
            self.return_mean += delta / self.return_count
            self.return_m2 += delta * (bar_return - self.return_mean)

        self.prev_curve_value = curve_value


class TradingViewLikeBacktester:
    """Backtester that mirrors TradingView's default broker-emulator assumptions."""

    def __init__(
        self,
        candle_request: CandleRequest,
        initial_equity: float = 100_000.0,
    ) -> None:
        self.candle_request = candle_request
        self.initial_equity = float(initial_equity)
        mintick = f"{self.candle_request.mintick:.10f}".rstrip("0").rstrip(".")
        self._price_decimals = max(0, len(mintick.split(".")[-1])) if "." in mintick else 0

    def run(
        self,
        signal_frame: pd.DataFrame | _CompiledSignalFrame,
        risk: RiskParameters,
        mode: Mode,
    ) -> BacktestResult:
        compiled = self.compile_signal_frame(signal_frame)
        metrics, trades, equity_curve = self._simulate(compiled, risk, mode, include_details=True)
        return BacktestResult(metrics=metrics, trades=trades, equity_curve=equity_curve)

    def run_metrics(
        self,
        signal_frame: pd.DataFrame | _CompiledSignalFrame,
        risk: RiskParameters,
        mode: Mode,
    ) -> BacktestMetrics:
        compiled = self.compile_signal_frame(signal_frame)
        metrics, _, _ = self._simulate(compiled, risk, mode, include_details=False)
        return metrics

    def compile_signal_frame(self, signal_frame: pd.DataFrame | _CompiledSignalFrame) -> _CompiledSignalFrame:
        if isinstance(signal_frame, _CompiledSignalFrame):
            return signal_frame

        dataframe = signal_frame.reset_index(drop=True)
        decimals = self._price_decimals
        time_values = dataframe["time"].to_numpy(dtype=np.int64, copy=True)
        end_date = None
        if time_values.size:
            end_date = pd.Timestamp(int(time_values.max()), unit="s", tz="UTC").strftime("%Y-%m-%d")

        return _CompiledSignalFrame(
            time=time_values.tolist(),
            open=dataframe["open"].round(decimals).to_numpy(dtype=np.float64).tolist(),
            high=dataframe["high"].round(decimals).to_numpy(dtype=np.float64).tolist(),
            low=dataframe["low"].round(decimals).to_numpy(dtype=np.float64).tolist(),
            close=dataframe["close"].round(decimals).to_numpy(dtype=np.float64).tolist(),
            in_date_range=dataframe["in_date_range"].fillna(False).tolist(),
            buy_signal=dataframe["buy_signal"].fillna(False).tolist(),
            sell_signal=dataframe["sell_signal"].fillna(False).tolist(),
            enable_long=dataframe["enable_long"].fillna(False).tolist(),
            enable_short=dataframe["enable_short"].fillna(False).tolist(),
            dynamic_stop_price=_optional_float_list(dataframe.get("dynamic_stop_price"), len(dataframe)),
            dynamic_target_price=_optional_float_list(dataframe.get("dynamic_target_price"), len(dataframe)),
            end_date=end_date,
            length=int(time_values.size),
        )

    def _simulate(
        self,
        signal_frame: _CompiledSignalFrame,
        risk: RiskParameters,
        mode: Mode,
        *,
        include_details: bool,
    ) -> tuple[BacktestMetrics, list[Trade], list[float]]:
        pending: _PendingOrder | None = None
        position: _Position | None = None
        equity = self.initial_equity
        stats = _MetricsAccumulator.create(self.initial_equity)
        equity_curve: list[float] = [equity] if include_details else []
        trades: list[Trade] = [] if include_details else []

        # Signal frame already holds Python lists — use directly.
        length = signal_frame.length
        times = signal_frame.time
        opens = signal_frame.open
        highs = signal_frame.high
        lows = signal_frame.low
        closes = signal_frame.close
        in_date_range_list = signal_frame.in_date_range
        buy_signals = signal_frame.buy_signal
        sell_signals = signal_frame.sell_signal
        enable_longs = signal_frame.enable_long
        enable_shorts = signal_frame.enable_short
        dynamic_stops = signal_frame.dynamic_stop_price
        dynamic_targets = signal_frame.dynamic_target_price
        last_index = length - 1

        for index in range(length):
            bar_time = times[index]
            open_price = opens[index]
            high_price = highs[index]
            low_price = lows[index]
            close_price = closes[index]

            position, equity, filled_trade = self._apply_pending_order(
                position, pending, bar_time, open_price, risk, equity,
            )
            pending = None
            if filled_trade is not None:
                stats.record_trade(filled_trade)
                if include_details:
                    trades.append(filled_trade)

            if position is not None:
                exit_price, exit_reason = self._check_bar_exit(position, open_price, high_price, low_price, close_price)
                if exit_price is not None:
                    trade, equity = self._close_position(position, bar_time, exit_price, exit_reason, equity)
                    stats.record_trade(trade)
                    if include_details:
                        trades.append(trade)
                    position = None

            curve_value = self._mark_to_market(equity, position, close_price)
            stats.observe_equity(curve_value)
            if include_details:
                equity_curve.append(curve_value)

            # Skip building a pending order on the last bar — it can never be filled
            if index < last_index:
                pending = self._build_next_order(
                    in_date_range=in_date_range_list[index],
                    buy_signal=buy_signals[index],
                    sell_signal=sell_signals[index],
                    enable_long=enable_longs[index],
                    enable_short=enable_shorts[index],
                    close_price=close_price,
                    dynamic_stop_price=dynamic_stops[index],
                    dynamic_target_price=dynamic_targets[index],
                    mode=mode,
                )

        metrics = self._build_metrics(stats, risk, mode, signal_frame.end_date)
        return metrics, trades, equity_curve

    def _apply_pending_order(
        self,
        position: _Position | None,
        pending: _PendingOrder | None,
        bar_time: int,
        open_price: float,
        risk: RiskParameters,
        equity: float,
    ) -> tuple[_Position | None, float, Trade | None]:
        if pending is None:
            return position, equity, None

        filled_trade: Trade | None = None

        if pending.action == "open_long":
            if position is not None and position.direction == "short":
                filled_trade, equity = self._close_position(position, bar_time, open_price, "reverse_to_long", equity)
                position = None
            if position is None:
                dynamic_stop = pending.dynamic_stop_price
                dynamic_target = pending.dynamic_target_price
                if (
                    dynamic_stop is not None and dynamic_target is not None
                    and dynamic_stop < open_price < dynamic_target
                ):
                    stop_price = dynamic_stop
                    target_price = dynamic_target
                else:
                    sl_offset = pending.signal_close * (risk.long_stoploss_pct / 100.0)
                    tp_offset = pending.signal_close * (risk.long_takeprofit_pct / 100.0)
                    stop_price = open_price - sl_offset
                    target_price = open_price + tp_offset
                position = _Position(
                    direction="long",
                    entry_time=bar_time,
                    entry_price=open_price,
                    stop_price=stop_price,
                    target_price=target_price,
                    equity_before=equity,
                )
        elif pending.action == "open_short":
            if position is not None and position.direction == "long":
                filled_trade, equity = self._close_position(position, bar_time, open_price, "reverse_to_short", equity)
                position = None
            if position is None:
                dynamic_stop = pending.dynamic_stop_price
                dynamic_target = pending.dynamic_target_price
                if (
                    dynamic_stop is not None and dynamic_target is not None
                    and dynamic_target < open_price < dynamic_stop
                ):
                    stop_price = dynamic_stop
                    target_price = dynamic_target
                else:
                    sl_offset = pending.signal_close * (risk.short_stoploss_pct / 100.0)
                    tp_offset = pending.signal_close * (risk.short_takeprofit_pct / 100.0)
                    stop_price = open_price + sl_offset
                    target_price = open_price - tp_offset
                position = _Position(
                    direction="short",
                    entry_time=bar_time,
                    entry_price=open_price,
                    stop_price=stop_price,
                    target_price=target_price,
                    equity_before=equity,
                )

        return position, equity, filled_trade

    def _check_bar_exit(
        self,
        position: _Position,
        open_price: float,
        high_price: float,
        low_price: float,
        close_price: float,
    ) -> tuple[float | None, str | None]:
        sl = position.stop_price
        tp = position.target_price

        # Approximate intrabar path: high before low when open is nearer to high
        if abs(open_price - high_price) <= abs(open_price - low_price):
            path = (open_price, high_price, low_price, close_price)
        else:
            path = (open_price, low_price, high_price, close_price)

        for start, end in zip(path, path[1:]):
            lo = min(start, end)
            hi = max(start, end)
            sl_hit = lo <= sl <= hi
            tp_hit = lo <= tp <= hi
            if not (sl_hit or tp_hit):
                continue
            if sl_hit and tp_hit:
                # Both levels in range: return whichever is encountered first
                first_hit = min(sl, tp) if end >= start else max(sl, tp)
                return first_hit, "stop_loss" if first_hit == sl else "take_profit"
            return (sl, "stop_loss") if sl_hit else (tp, "take_profit")

        return None, None

    def _build_next_order(
        self,
        *,
        in_date_range: bool,
        buy_signal: bool,
        sell_signal: bool,
        enable_long: bool,
        enable_short: bool,
        close_price: float,
        dynamic_stop_price: float | None,
        dynamic_target_price: float | None,
        mode: Mode,
    ) -> _PendingOrder | None:
        if not in_date_range:
            return None

        long_allowed = enable_long and mode in {"long", "both"}
        short_allowed = enable_short and mode in {"short", "both"}

        if buy_signal and long_allowed and not sell_signal:
            return _PendingOrder(
                "open_long",
                signal_close=close_price,
                dynamic_stop_price=dynamic_stop_price,
                dynamic_target_price=dynamic_target_price,
            )
        if sell_signal and short_allowed and not buy_signal:
            return _PendingOrder(
                "open_short",
                signal_close=close_price,
                dynamic_stop_price=dynamic_stop_price,
                dynamic_target_price=dynamic_target_price,
            )
        return None

    def _close_position(
        self,
        position: _Position,
        exit_time: int,
        exit_price: float,
        exit_reason: str,
        equity: float,
    ) -> tuple[Trade, float]:
        if position.direction == "long":
            return_pct = ((exit_price - position.entry_price) / position.entry_price) * 100.0
        else:
            return_pct = ((position.entry_price - exit_price) / position.entry_price) * 100.0

        equity_after = equity * (1.0 + return_pct / 100.0)
        trade = Trade(
            entry_time=position.entry_time,
            exit_time=exit_time,
            direction=position.direction,
            entry_price=position.entry_price,
            exit_price=exit_price,
            exit_reason=exit_reason,
            return_pct=return_pct,
            equity_before=position.equity_before,
            equity_after=equity_after,
        )
        return trade, equity_after

    def _mark_to_market(self, equity: float, position: _Position | None, close_price: float) -> float:
        if position is None:
            return equity
        if position.direction == "long":
            return equity * (close_price / position.entry_price)
        return equity * (position.entry_price / close_price)

    def _build_metrics(
        self,
        stats: _MetricsAccumulator,
        risk: RiskParameters,
        mode: Mode,
        end_date: str | None,
    ) -> BacktestMetrics:
        win_rate = (stats.wins / stats.trade_count * 100.0) if stats.trade_count else 0.0
        if stats.positive_pnl <= 0.0:
            profit_factor = 0.0
        elif stats.negative_pnl == 0.0:
            profit_factor = float("inf")
        else:
            profit_factor = stats.positive_pnl / abs(stats.negative_pnl)

        sl_pct = risk.long_stoploss_pct if mode != "short" else risk.short_stoploss_pct
        tp_pct = risk.long_takeprofit_pct if mode != "short" else risk.short_takeprofit_pct
        final_equity = stats.final_closed_equity
        net_profit_pct = ((final_equity - self.initial_equity) / self.initial_equity) * 100.0

        avg_win = (stats.win_return_sum / stats.win_return_count) if stats.win_return_count else 0.0
        avg_loss = (stats.loss_return_sum / stats.loss_return_count) if stats.loss_return_count else 0.0
        expectancy = (stats.total_return_sum / stats.trade_count) if stats.trade_count else 0.0
        signal_exits = stats.trade_count - stats.sl_exits - stats.tp_exits
        n = stats.trade_count or 1
        sl_exit_pct = stats.sl_exits / n * 100.0
        tp_exit_pct = stats.tp_exits / n * 100.0
        signal_exit_pct = signal_exits / n * 100.0

        sharpe = 0.0
        if stats.return_count > 0:
            variance = stats.return_m2 / stats.return_count
            std_r = math.sqrt(variance)
            if std_r > 0:
                sharpe = (stats.return_mean / std_r) * _annualization_factor(self.candle_request.timeframe)

        calmar = 0.0
        if stats.max_drawdown > 0:
            calmar = net_profit_pct / stats.max_drawdown

        return BacktestMetrics(
            symbol=f"{self.candle_request.exchange}:{self.candle_request.symbol}",
            timeframe=self.candle_request.timeframe,
            start=self.candle_request.start,
            end=self.candle_request.end or end_date,
            mode=mode,
            sl_pct=round(sl_pct, 2),
            tp_pct=round(tp_pct, 2),
            net_profit_pct=round(net_profit_pct, 2),
            max_drawdown_pct=round(stats.max_drawdown, 2),
            win_rate_pct=round(win_rate, 2),
            profit_factor=round(profit_factor, 2) if profit_factor != float("inf") else profit_factor,
            trade_count=stats.trade_count,
            equity_final=round(final_equity, 2),
            sharpe_ratio=round(sharpe, 2),
            calmar_ratio=round(calmar, 2),
            expectancy_pct=round(expectancy, 2),
            avg_win_pct=round(avg_win, 2),
            avg_loss_pct=round(avg_loss, 2),
            worst_trade_pct=round(stats.worst_trade if stats.trade_count else 0.0, 2),
            max_consec_losses=stats.max_consec_losses,
            sl_exit_pct=round(sl_exit_pct, 2),
            tp_exit_pct=round(tp_exit_pct, 2),
            signal_exit_pct=round(signal_exit_pct, 2),
        )


def _optional_float_list(series: pd.Series | None, length: int) -> list[float | None]:
    if series is None:
        return [None] * length
    output: list[float | None] = []
    for value in series.tolist():
        if value is None or pd.isna(value):
            output.append(None)
        else:
            output.append(float(value))
    return output
