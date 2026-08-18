from __future__ import annotations

import argparse
import time
from typing import TYPE_CHECKING

import pandas as pd

from ..downloader import TradingViewDataClient
from ..utils import format_time
from strategy import get_strategy, BaseStrategy

if TYPE_CHECKING:
    from ..models import CandleRequest


def _resolve(args: argparse.Namespace, config: dict, key: str, default=None):
    """Return CLI override if set, else config value, else default."""
    cli_value = getattr(args, key, None)
    if cli_value is not None:
        return cli_value
    return config.get(key, default)


def parse_pair(entry: str) -> tuple[str, str]:
    """Parse 'EXCHANGE:SYMBOL' into (symbol, exchange)."""
    if ":" not in entry:
        raise SystemExit(
            f"Error: Invalid pair format '{entry}'. "
            f"Expected 'EXCHANGE:SYMBOL' (e.g. 'NASDAQ:AAPL')."
        )
    exchange, symbol = entry.split(":", 1)
    exchange, symbol = exchange.strip(), symbol.strip()
    if not exchange or not symbol:
        raise SystemExit(f"Error: Invalid pair format '{entry}'. Expected 'EXCHANGE:SYMBOL'.")
    return symbol, exchange


def resolve_pairlist(args: argparse.Namespace, config: dict) -> list[tuple[str, str]]:
    """Return list of (symbol, exchange) tuples from --pairs, --symbol, or config pairlist."""
    # Explicit --pairs (download-data)
    pairs_arg = getattr(args, "pairs", None)
    if pairs_arg:
        return [parse_pair(p) for p in pairs_arg]
    # Explicit --symbol (backtest / hyperopt)
    symbol = getattr(args, "symbol", None)
    if symbol:
        return [parse_pair(symbol)]
    # Fall back to config pairlist
    entries = config.get("pairlist", [])
    if not entries:
        raise SystemExit(
            "Error: No pairs specified. Either use --pairs / --symbol on the CLI,\n"
            "or define a 'pairlist' in your config file."
        )
    return [parse_pair(e) for e in entries]


def load_candles(
    candle_request: "CandleRequest",
    data_dir: str,
    *,
    step: str = "",
    quiet: bool = False,
    compact: bool = False,
) -> pd.DataFrame:
    """Load cached candle data and print progress."""
    if not quiet and not compact:
        print(f"\n[{step}] Loading candle data...")
    t0 = time.time()
    client = TradingViewDataClient(cache_dir=data_dir)
    candles = client.get_history(candle_request, cache_only=True)
    if not quiet and not compact:
        print(f"      {len(candles)} candles loaded ({format_time(time.time() - t0)})")
    if compact:
        print(f"   \u2022 Data    : {len(candles):,} candles loaded ({format_time(time.time() - t0)})")
    return candles


def generate_signals(
    strategy_name: str,
    candles: pd.DataFrame,
    mode: str,
    start: str | None,
    end: str | None,
    strategy_settings: dict | None = None,
    *,
    step: str = "",
    quiet: bool = False,
    compact: bool = False,
    density_suffix: str = "",
) -> tuple[pd.DataFrame, BaseStrategy]:
    """Instantiate strategy, generate signals, and print progress."""
    if not quiet and not compact:
        print(f"\n[{step}] Generating signals...")
    t0 = time.time()
    strategy = get_strategy(strategy_name)
    signal_settings = {
        "enable_long": mode in {"long", "both"},
        "enable_short": mode in {"short", "both"},
        "start": start,
        "end": end,
    }
    if strategy_settings:
        signal_settings.update(strategy_settings)
    signal_frame = strategy.generate_signals(candles, signal_settings)
    buy_count = int(signal_frame["buy_signal"].sum())
    sell_count = int(signal_frame["sell_signal"].sum())
    if not quiet and not compact:
        print(f"      {buy_count} buy / {sell_count} sell signals ({format_time(time.time() - t0)})")
    if compact:
        print(f"   \u2022 Signals : {buy_count} buy / {sell_count} sell{density_suffix}")
    return signal_frame, strategy


# ---------------------------------------------------------------------------
# Compact hyperopt results table (rich)
# ---------------------------------------------------------------------------

def _hyperopt_arrow(value: float, fmt: str = ".1f", *, invert: bool = False) -> str:
    """Return an arrow-decorated string for rich markup (hyperopt variant)."""
    suffix = "%"
    if invert:
        return f"[red]▼ {abs(value):{fmt}}{suffix}[/red]"
    if value > 0:
        return f"[green]▲ {value:{fmt}}{suffix}[/green]"
    if value < 0:
        return f"[red]▼ {abs(value):{fmt}}{suffix}[/red]"
    return f"{value:{fmt}}{suffix}"


def print_hyperopt_table(
    results: list,
    top_n: int,
) -> None:
    """Print a rich-formatted table of top hyperopt results."""
    from rich.console import Console
    from rich.table import Table
    import rich.box

    if not results:
        return

    shown = results[:top_n]
    n = len(shown)
    console = Console()

    table = Table(
        title=f"\U0001f3c6 Top {n} Optimization Results",
        title_style="bold",
        box=rich.box.ROUNDED,
        pad_edge=True,
        show_lines=False,
    )

    # Parameter columns (cyan styling)
    table.add_column("SL %", justify="right", style="cyan", no_wrap=True)
    table.add_column("TP %", justify="right", style="cyan", no_wrap=True)
    # Metric columns
    table.add_column("Return", justify="right", no_wrap=True)
    table.add_column("Max DD", justify="right", no_wrap=True)
    table.add_column("Shrp", justify="right", no_wrap=True)
    table.add_column("Win %", justify="right", no_wrap=True)
    table.add_column("PF", justify="right", no_wrap=True)
    table.add_column("Trds", justify="right", no_wrap=True)
    table.add_column("Final Eq.", justify="right", no_wrap=True)

    for m in shown:
        pf_str = f"{m.profit_factor:.2f}" if m.profit_factor != float("inf") else "∞"
        table.add_row(
            f"{m.sl_pct:.2f}",
            f"{m.tp_pct:.2f}",
            _hyperopt_arrow(m.net_profit_pct),
            _hyperopt_arrow(m.max_drawdown_pct, invert=True),
            f"{m.sharpe_ratio:.2f}",
            f"{m.win_rate_pct:.1f}%",
            pf_str,
            str(m.trade_count),
            f"${m.equity_final:,.0f}",
        )

    console.print()
    console.print(table, justify="left")


# ---------------------------------------------------------------------------
# Shared summary table (rich)
# ---------------------------------------------------------------------------

def _arrow(value: float, fmt: str = ".1f", *, pct: bool = True, invert: bool = False) -> str:
    """Return an arrow-decorated string for rich markup.

    Parameters
    ----------
    value : float
        The numeric value to display.
    fmt : str
        Format spec for the number (default ".1f").
    pct : bool
        Whether to append a percent sign.
    invert : bool
        If True, positive is bad (red) and negative is good (green) — used for
        drawdown / worst-trade where the value is already negative or represents loss.
    """
    suffix = "%" if pct else ""
    if invert:
        return f"[red]▼ {abs(value):{fmt}}{suffix}[/red]"
    formatted = f"{value:{fmt}}{suffix}"
    if value > 0:
        return f"[green]▲ {formatted}[/green]"
    if value < 0:
        return f"[red]▼ {abs(value):{fmt}}{suffix}[/red]"
    return formatted


def _compute_portfolio_aggregate(
    all_results: list[tuple[str, str, "BacktestResult"]],
    all_trades: list,
    equity_curves: list[list[float]],
    initial_equity: float,
) -> dict:
    """Compute aggregate portfolio metrics from per-pair results."""
    import math
    from ..backtest.engine import _annualization_factor

    n = len(all_results)

    # Combined equity curve: sum bar-by-bar, pad shorter curves with last value.
    max_len = max(len(ec) for ec in equity_curves)
    combined = [0.0] * max_len
    for ec in equity_curves:
        last = ec[-1] if ec else initial_equity
        for j in range(max_len):
            combined[j] += ec[j] if j < len(ec) else last

    total_initial = initial_equity * n
    total_final = sum(r.metrics.equity_final for _, _, r in all_results)
    port_return = ((total_final - total_initial) / total_initial) * 100.0

    # Max drawdown from combined curve
    peak = combined[0]
    max_dd = 0.0
    for v in combined:
        if v > peak:
            peak = v
        if peak > 0:
            dd = ((peak - v) / peak) * 100.0
            if dd > max_dd:
                max_dd = dd

    # Sharpe from bar returns
    sharpe = 0.0
    if len(combined) > 1:
        returns = [
            (combined[j] - combined[j - 1]) / combined[j - 1]
            for j in range(1, len(combined))
            if combined[j - 1] != 0
        ]
        if returns:
            mean_r = sum(returns) / len(returns)
            var_r = sum((r - mean_r) ** 2 for r in returns) / len(returns)
            std_r = math.sqrt(var_r)
            if std_r > 0:
                tf = all_results[0][2].metrics.timeframe
                sharpe = (mean_r / std_r) * _annualization_factor(tf)

    calmar = port_return / max_dd if max_dd > 0 else 0.0

    # Trade statistics from combined pool
    total_trades = len(all_trades)
    wins = [t for t in all_trades if t.return_pct >= 0]
    losses = [t for t in all_trades if t.return_pct < 0]
    win_rate = (len(wins) / total_trades * 100.0) if total_trades else 0.0

    gross_win = sum(t.return_pct for t in wins)
    gross_loss = sum(abs(t.return_pct) for t in losses)
    pf = (gross_win / gross_loss) if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0)
    total_return_sum = sum(t.return_pct for t in all_trades)
    exp = (total_return_sum / total_trades) if total_trades else 0.0
    avg_w = (gross_win / len(wins)) if wins else 0.0
    avg_l = (-gross_loss / len(losses)) if losses else 0.0
    worst = min((t.return_pct for t in all_trades), default=0.0)
    mcl = max(r.metrics.max_consec_losses for _, _, r in all_results)

    # Exit breakdown
    total_sl = sum(round(r.metrics.sl_exit_pct / 100 * r.metrics.trade_count) for _, _, r in all_results)
    total_tp = sum(round(r.metrics.tp_exit_pct / 100 * r.metrics.trade_count) for _, _, r in all_results)
    total_sig = total_trades - total_sl - total_tp
    if total_trades > 0:
        sl_p, tp_p, sig_p = (
            total_sl / total_trades * 100,
            total_tp / total_trades * 100,
            total_sig / total_trades * 100,
        )
    else:
        sl_p = tp_p = sig_p = 0.0

    return {
        "return": port_return, "max_dd": max_dd, "sharpe": sharpe,
        "calmar": calmar, "win_rate": win_rate, "pf": pf, "exp": exp,
        "avg_w": avg_w, "avg_l": avg_l, "worst": worst, "mcl": mcl,
        "trades": total_trades, "sl_tp_sig": f"{sl_p:.0f}/{tp_p:.0f}/{sig_p:.0f}",
        "final": total_final,
    }


def print_summary_table(
    all_results: list[tuple[str, str, "BacktestResult"]],
    *,
    initial_equity: float = 100_000.0,
    title: str = "BACKTEST SUMMARY",
) -> None:
    """Print a rich-formatted summary table with a true PORTFOLIO aggregate row."""
    from ..models import BacktestResult  # noqa: lazy import

    import rich.box
    from rich.console import Console
    from rich.table import Table

    if not all_results:
        return

    console = Console()

    # ── Build the table ──────────────────────────────────────────────
    table = Table(
        title=f"📊 {title}",
        title_style="bold",
        show_lines=False,
        pad_edge=True,
        box=rich.box.ROUNDED,
    )

    table.add_column("#", justify="right", style="dim", no_wrap=True)
    table.add_column("Pair", justify="left", no_wrap=True)
    table.add_column("Return", justify="right", no_wrap=True)
    table.add_column("Max DD", justify="right", no_wrap=True)
    table.add_column("Shrp", justify="right", no_wrap=True)
    table.add_column("Cal", justify="right", no_wrap=True)
    table.add_column("Win %", justify="right", no_wrap=True)
    table.add_column("PF", justify="right", no_wrap=True)
    table.add_column("Expect", justify="right", no_wrap=True)
    table.add_column("Avg W/L %", justify="right", no_wrap=True)
    table.add_column("Worst", justify="right", no_wrap=True)
    table.add_column("L.S", justify="right", no_wrap=True)
    table.add_column("Trds", justify="right", no_wrap=True)
    table.add_column("SL/TP/S", justify="right", no_wrap=True)
    table.add_column("Final Eq.", justify="right", no_wrap=True)

    # ── Helper to format a single data row ───────────────────────────
    def _row(
        idx: str,
        pair: str,
        m_net: float,
        m_dd: float,
        m_sharpe: float,
        m_calmar: float,
        m_wr: float,
        m_pf: float,
        m_exp: float,
        m_avg_w: float,
        m_avg_l: float,
        m_worst: float,
        m_mcl: int,
        m_trades: int,
        m_sl_tp_sig: str,
        m_eq: float,
        *,
        is_portfolio: bool = False,
    ) -> list[str]:
        pf_str = f"{m_pf:.2f}" if m_pf != float("inf") else "∞"
        avg_wl = f"+{m_avg_w:.1f}/{m_avg_l:.1f}" if m_avg_l <= 0 else f"+{m_avg_w:.1f}/+{m_avg_l:.1f}"
        style = "bold" if is_portfolio else ""
        return [
            idx,
            f"[{style}]{pair}[/{style}]" if style else pair,
            _arrow(m_net),
            _arrow(m_dd, invert=True),
            f"{m_sharpe:.2f}",
            f"{m_calmar:.1f}" if abs(m_calmar) < 100 else f"{m_calmar:.0f}",
            f"{m_wr:.1f}%",
            pf_str,
            _arrow(m_exp),
            avg_wl,
            _arrow(m_worst, invert=True),
            str(m_mcl),
            str(m_trades),
            m_sl_tp_sig,
            f"${m_eq:,.0f}",
        ]

    # ── Add per-pair rows ────────────────────────────────────────────
    all_trades_combined = []
    all_equity_curves = []

    for i, (symbol, exchange, result) in enumerate(all_results, 1):
        m = result.metrics
        pair = f"{exchange}:{symbol}"
        sl_tp_sig = f"{m.sl_exit_pct:.0f}/{m.tp_exit_pct:.0f}/{m.signal_exit_pct:.0f}"

        table.add_row(*_row(
            str(i), pair, m.net_profit_pct, m.max_drawdown_pct,
            m.sharpe_ratio, m.calmar_ratio, m.win_rate_pct, m.profit_factor,
            m.expectancy_pct, m.avg_win_pct, m.avg_loss_pct, m.worst_trade_pct,
            m.max_consec_losses, m.trade_count, sl_tp_sig, m.equity_final,
        ))

        all_trades_combined.extend(result.trades)
        all_equity_curves.append(result.equity_curve)

    # ── PORTFOLIO aggregate row (only when multiple pairs) ───────────
    n = len(all_results)
    if n > 1:
        table.add_section()
        p = _compute_portfolio_aggregate(all_results, all_trades_combined, all_equity_curves, initial_equity)
        table.add_row(*_row(
            "*", "PORTFOLIO", p["return"], p["max_dd"],
            p["sharpe"], p["calmar"], p["win_rate"], p["pf"],
            p["exp"], p["avg_w"], p["avg_l"], p["worst"],
            p["mcl"], p["trades"], p["sl_tp_sig"], p["final"],
            is_portfolio=True,
        ))

    console.print()
    console.print(table)
    console.print()
