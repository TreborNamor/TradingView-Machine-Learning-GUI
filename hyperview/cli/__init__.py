from __future__ import annotations

import argparse

from ..config import load_config
from .download import run_download_data
from .backtest import run_backtest
from .hyperopt import run_hyperopt
from .pine import run_pine_analyze_best_when, run_pine_batch_optimize, run_pine_optimize
from .list import run_list_data, run_list_strategies


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hyperview",
        description="HyperView - CLI-driven TradingView strategy backtester and hyper-optimizer",
    )
    parser.add_argument("--config", default=None, help="Path to config.json (default: auto-detect)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ------ download-data ------
    dl = subparsers.add_parser("download-data", help="Download candle data for one or more pairs")
    dl.add_argument("--pairs", nargs="+", default=None, help="Pairs to download (e.g. NASDAQ:NFLX COINBASE:BTCUSD); falls back to config pairlist")
    dl.add_argument(
        "--timeframe",
        nargs="+",
        default=None,
        help="One or more bar intervals to download (e.g. 1h 15m); falls back to config timeframe",
    )
    dl.add_argument("--start", default=None)
    dl.add_argument("--end", default=None)
    dl.add_argument("--session", default=None)
    dl.add_argument("--adjustment", default="splits", help="Price adjustment: splits, dividends, none (default: splits)")

    # ------ backtest ------
    bt = subparsers.add_parser("backtest", help="Run a single backtest with fixed SL/TP")
    bt.add_argument("--symbol", default=None, help="Single pair to backtest (e.g. NASDAQ:TSLA); falls back to config pairlist")
    bt.add_argument("--timeframe", default=None)
    bt.add_argument("--start", default=None)
    bt.add_argument("--end", default=None)
    bt.add_argument("--session", default=None)
    bt.add_argument("--adjustment", default="splits", help="Price adjustment: splits, dividends, none (default: splits)")
    bt.add_argument("--strategy", default=None, help="Strategy name (default: from config)")
    bt.add_argument("--preset-file", default=None, help="Path to a strategy preset file created by hyperopt")
    bt.add_argument("--preset-rank", type=int, default=None, help="Preset rank to use when a context has multiple presets (default: best rank)")
    bt.add_argument("--sl", type=float, default=None, help="Stop-loss %% (falls back to matching preset file entry)")
    bt.add_argument("--tp", type=float, default=None, help="Take-profit %% (falls back to matching preset file entry)")
    bt.add_argument("--mode", choices=["long", "short", "both"], default=None)

    # ------ hyperopt ------
    ho = subparsers.add_parser("hyperopt", help="Hyper-optimize SL/TP parameters")
    ho.add_argument("--symbol", default=None, help="Single pair to optimize (e.g. NASDAQ:TSLA); falls back to config pairlist")
    ho.add_argument("--timeframe", default=None)
    ho.add_argument("--start", default=None)
    ho.add_argument("--end", default=None)
    ho.add_argument("--session", default=None)
    ho.add_argument("--adjustment", default="splits", help="Price adjustment: splits, dividends, none (default: splits)")
    ho.add_argument("--strategy", default=None, help="Strategy name (default: from config)")
    ho.add_argument("--sl-min", type=float, default=None)
    ho.add_argument("--sl-max", type=float, default=None)
    ho.add_argument("--tp-min", type=float, default=None)
    ho.add_argument("--tp-max", type=float, default=None)
    ho.add_argument("--mode", choices=["long", "short", "both"], default=None)
    ho.add_argument(
        "--objective",
        choices=["net_profit_pct", "profit_factor", "win_rate_pct", "max_drawdown_pct", "trade_count"],
        default=None,
    )
    ho.add_argument("--top-n", type=int, default=None)
    ho.add_argument(
        "--n-trials",
        type=int,
        default=None,
        help="Number of Bayesian optimization trials (default: from config or 200)",
    )

    # ------ pine-optimize ------
    po = subparsers.add_parser("pine-optimize", help="Optimize full Pine strategy input space with adaptive 2-stage search")
    po.add_argument("--pine-file", required=True, help="Path to Pine strategy file (e.g. smc_swing_strategy.pine)")
    po.add_argument("--symbol", default=None, help="Single pair (EXCHANGE:SYMBOL); falls back to config pairlist")
    po.add_argument("--timeframe", default=None)
    po.add_argument("--start", default=None)
    po.add_argument("--end", default=None)
    po.add_argument("--session", default=None)
    po.add_argument("--adjustment", default="splits")
    po.add_argument("--strategy", default="smc_swing")
    po.add_argument("--mode", choices=["long", "short", "both"], default=None)
    po.add_argument("--objective", choices=["net_profit_pct", "profit_factor", "win_rate_pct", "max_drawdown_pct", "trade_count"], default=None)
    po.add_argument("--coarse-trials", type=int, default=None)
    po.add_argument("--fine-trials", type=int, default=None)
    po.add_argument("--coarse-top-k", type=int, default=None)
    po.add_argument("--preset-top-n", type=int, default=None)
    po.add_argument("--min-trades", type=int, default=None)
    po.add_argument("--min-signals", type=int, default=None)
    po.add_argument("--budget-minutes", type=int, default=None)
    po.add_argument("--watchdog-seconds", type=int, default=None)
    po.add_argument("--fine-span-ratio", type=float, default=None)
    po.add_argument("--sl", type=float, default=None, help="Fallback static SL%% if dynamic levels are unavailable")
    po.add_argument("--tp", type=float, default=None, help="Fallback static TP%% if dynamic levels are unavailable")
    po.add_argument("--preset-file", default=None, help="Output preset file path (default: <output_dir>/<strategy>_presets.json)")
    po.add_argument("--report-dir", default=None, help="Output folder for JSON/MD/CSV reports")
    po.add_argument(
        "--emit-optimized-pine",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Emit optimized .pine with best params injected (default: true)",
    )
    po.add_argument("--optimized-dir", default="strategies/optimized", help="Output directory for optimized .pine files")
    po.add_argument(
        "--filename-template",
        default="{symbol}_{tf}_{strategy}_np{net}_dd{dd}_pf{pf}_tc{trades}.pine",
        help="Filename template for optimized .pine files",
    )

    # ------ pine-batch-optimize ------
    pb = subparsers.add_parser("pine-batch-optimize", help="Batch optimize all .pine files in a directory")
    pb.add_argument("--input-dir", default="strategies/raw", help="Directory containing source .pine strategy files")
    pb.add_argument("--symbols", nargs="+", default=None, help="Symbols (EXCHANGE:SYMBOL). Falls back to config pairlist")
    pb.add_argument("--timeframes", nargs="+", default=None, help="One or more timeframes (falls back to config timeframe)")
    pb.add_argument("--start", default=None)
    pb.add_argument("--end", default=None)
    pb.add_argument("--session", default=None)
    pb.add_argument("--adjustment", default="splits")
    pb.add_argument("--strategy", default="smc_swing")
    pb.add_argument("--mode", choices=["long", "short", "both"], default=None)
    pb.add_argument("--objective", choices=["net_profit_pct", "profit_factor", "win_rate_pct", "max_drawdown_pct", "trade_count"], default=None)
    pb.add_argument("--coarse-trials", type=int, default=None)
    pb.add_argument("--fine-trials", type=int, default=None)
    pb.add_argument("--coarse-top-k", type=int, default=None)
    pb.add_argument("--preset-top-n", type=int, default=None)
    pb.add_argument("--min-trades", type=int, default=None)
    pb.add_argument("--min-signals", type=int, default=None)
    pb.add_argument("--budget-minutes", type=int, default=None)
    pb.add_argument("--watchdog-seconds", type=int, default=None)
    pb.add_argument("--fine-span-ratio", type=float, default=None)
    pb.add_argument("--sl", type=float, default=None)
    pb.add_argument("--tp", type=float, default=None)
    pb.add_argument("--preset-file", default=None)
    pb.add_argument("--report-root", default=None, help="Root directory for batch reports (default: <output_dir>/optimizations)")
    pb.add_argument(
        "--emit-optimized-pine",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Emit optimized .pine with best params injected (default: true)",
    )
    pb.add_argument("--optimized-dir", default="strategies/optimized", help="Output directory for optimized .pine files")
    pb.add_argument(
        "--filename-template",
        default="{symbol}_{tf}_{strategy}_np{net}_dd{dd}_pf{pf}_tc{trades}.pine",
        help="Filename template for optimized .pine files",
    )

    # ------ pine-analyze-best-when ------
    pa = subparsers.add_parser("pine-analyze-best-when", help="Re-analyze best trading windows from saved pine optimization context")
    pa.add_argument("--preset-file", default=None, help="Preset file used to infer context path")
    pa.add_argument("--context-file", default=None, help="Explicit context JSON from pine-optimize")
    pa.add_argument("--min-trades", type=int, default=None, help="Minimum trade count gate for ranking buckets")
    pa.add_argument("--report-dir", default=None, help="Output folder for refreshed reports")
    # ------ list-data ------
    subparsers.add_parser("list-data", help="List cached candle datasets")

    # ------ list-strategies ------
    subparsers.add_parser("list-strategies", help="List registered strategies")

    return parser


_COMMANDS = {
    "download-data": run_download_data,
    "backtest": run_backtest,
    "hyperopt": run_hyperopt,
    "pine-optimize": run_pine_optimize,
    "pine-batch-optimize": run_pine_batch_optimize,
    "pine-analyze-best-when": run_pine_analyze_best_when,
    "list-data": run_list_data,
    "list-strategies": run_list_strategies,
}


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config(args.config)
    handler = _COMMANDS.get(args.command)
    if handler is None:
        parser.error(f"unknown command: {args.command}")
        return 1
    return handler(args, config)
