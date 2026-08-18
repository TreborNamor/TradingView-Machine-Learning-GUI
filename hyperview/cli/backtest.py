from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path

from rich.console import Console

from ..models import BacktestMetrics, BacktestResult, CandleRequest, RiskParameters
from ..presets import find_preset, strategy_preset_path
from ..backtest.engine import TradingViewLikeBacktester
from ..utils import format_time
from .formatting import _resolve, load_candles, generate_signals, resolve_pairlist, print_summary_table
from strategy import list_strategies


def _run_single_backtest(
    symbol: str,
    exchange: str,
    timeframe: str,
    session: str,
    adjustment: str,
    strategy_name: str,
    initial_capital: float,
    data_dir: str,
    mode: str,
    sl: float,
    tp: float,
    start: str | None,
    end: str | None,
    strategy_settings: dict | None = None,
    *,
    pair_index: int = 1,
    pair_total: int = 1,
) -> BacktestResult | None:
    
    pair_label = f"{exchange}:{symbol}"
    tag = f"[{pair_index}/{pair_total}] {pair_label}"
    dot_width = max(40 - len(tag), 3)
    prefix = f"\n   {tag} {'.' * dot_width} "
    print(prefix, end="", flush=True)

    candle_request = CandleRequest(
        symbol=symbol,
        exchange=exchange,
        timeframe=timeframe,
        start=start,
        end=end,
        session=session,
        adjustment=adjustment,
    )

    t_total = time.time()

    try:
        # 1. Load data
        candles = load_candles(candle_request, data_dir, step="1/3", quiet=True)
        if candles is None or len(candles) == 0:
            print("skipped (no candle data)")
            return None

        # 2. Generate signals
        signal_frame, _ = generate_signals(
            strategy_name,
            candles,
            mode,
            start,
            end,
            strategy_settings=strategy_settings,
            step="2/3",
            quiet=True,
        )
        if signal_frame is None or len(signal_frame) == 0:
            print("skipped (no signals generated)")
            return None

        # 3. Run backtest
        risk = RiskParameters.from_mode(mode, sl, tp)
        backtester = TradingViewLikeBacktester(
            candle_request=candle_request, 
            initial_equity=initial_capital
        )
        
        result = backtester.run(signal_frame, risk, mode)
        elapsed = format_time(time.time() - t_total)

        print(f"✔ {elapsed}")
        return result

    except Exception as e:
        print(f"✘ ({e})")
        logging.exception(f"Error during backtest of {pair_label}")
        return None


def run_backtest(args: argparse.Namespace, config: dict) -> int:
    strategy_name = _resolve(args, config, "strategy")
    available_strategies = list_strategies()
    
    if not strategy_name or strategy_name not in available_strategies:
        print("Error: Invalid or no strategy specified.")
        print(f"Available strategies: {', '.join(available_strategies) or '(none)'}")
        return 1

    timeframe = _resolve(args, config, "timeframe")
    session = _resolve(args, config, "session")
    mode = _resolve(args, config, "mode", "long")
    adjustment = args.adjustment
    initial_capital = config.get("initial_capital", 1000.0)
    data_dir = config.get("data_dir", "./data")
    output_dir = config.get("output_dir", "./results")
    strategy_settings = _resolve_strategy_settings(strategy_name, config, timeframe)

    _resolve_preset_file_path(args, output_dir, strategy_name)

    pairs = resolve_pairlist(args, config)
    if not pairs:
        print("Error: No trading pairs resolved. Please check your config or arguments.")
        return 1

    resolved_risk: dict[tuple[str, str], tuple[float, float]] = {}
    risk_source = "CLI values"
    for symbol, pair_exchange in pairs:
        try:
            sl, tp, pair_source = _resolve_backtest_risk(
                args=args,
                symbol=symbol,
                exchange=pair_exchange,
                strategy_name=strategy_name,
                timeframe=timeframe,
                session=session,
                adjustment=adjustment,
                mode=mode,
            )
        except ValueError as exc:
            print(f"Error: {exc}")
            return 1
        resolved_risk[(symbol, pair_exchange)] = (sl, tp)
        if pair_source != "cli":
            risk_source = "matching preset file entry"
        elif args.sl is None or args.tp is None:
            risk_source = "CLI/preset-file mixed fallback"

    console = Console()

    line = "─" * 72
    console.print(f"\n ⚙ CONFIGURATION")
    console.print(f" {line}")
    console.print(f"   Strategy : {strategy_name} (mode: {mode})")
    if args.sl is not None and args.tp is not None:
        console.print(f"   Risk     : SL={args.sl}% TP={args.tp}%")
    else:
        console.print(f"   Risk     : {risk_source}")
    console.print(f" {line}")
    console.print(f"\n ⏳ RUNNING BACKTEST ({len(pairs)} Pair{'s' if len(pairs) != 1 else ''})")

    all_results: list[tuple[str, str, BacktestResult]] = []
    rc = 0
    
    for idx, (symbol, pair_exchange) in enumerate(pairs, 1):
        sl, tp = resolved_risk[(symbol, pair_exchange)]
        result = _run_single_backtest(
            symbol=symbol,
            exchange=pair_exchange,
            timeframe=timeframe,
            session=session,
            adjustment=adjustment,
            strategy_name=strategy_name,
            initial_capital=initial_capital,
            data_dir=data_dir,
            mode=mode,
            sl=sl,
            tp=tp,
            start=args.start,
            end=args.end,
            strategy_settings=strategy_settings,
            pair_index=idx,
            pair_total=len(pairs),
        )
        if result is None:
            rc = 1
        else:
            all_results.append((symbol, pair_exchange, result))

    print_summary_table(all_results, initial_equity=initial_capital)

    return rc


def _resolve_backtest_risk(
    *,
    args: argparse.Namespace,
    symbol: str,
    exchange: str,
    strategy_name: str,
    timeframe: str,
    session: str,
    adjustment: str,
    mode: str,
) -> tuple[float, float, str]:
    pair = f"{exchange}:{symbol}"
    preset = None
    if args.preset_file is not None:
        try:
            preset = find_preset(
                args.preset_file,
                strategy=strategy_name,
                pair=pair,
                timeframe=timeframe,
                session=session,
                adjustment=adjustment,
                mode=mode,
                rank=getattr(args, "preset_rank", None),
            )
        except (FileNotFoundError, ValueError) as exc:
            raise ValueError(str(exc)) from exc

    sl = args.sl if args.sl is not None else (preset.get("sl") if preset is not None else None)
    tp = args.tp if args.tp is not None else (preset.get("tp") if preset is not None else None)
    if sl is None or tp is None:
        preset_hint = (
            f" or pass --preset-file {args.preset_file}"
            if args.preset_file is not None
            else " or pass --preset-file <path-to-strategy-presets.json>"
        )
        raise ValueError(
            f"Missing SL/TP for {pair}. Provide --sl and --tp{preset_hint}. "
            f"Expected a matching preset for timeframe={timeframe}, session={session}, "
            f"adjustment={adjustment}, mode={mode}."
        )
    source = "cli" if args.sl is not None and args.tp is not None else "preset"
    return float(sl), float(tp), source


def _resolve_preset_file_path(
    args: argparse.Namespace,
    output_dir: str,
    strategy_name: str,
) -> None:
    """Resolve --preset-file to an absolute path, falling back to the output dir."""
    if args.preset_file is not None:
        # If it's a bare filename (no directory separators), look in output_dir
        given = Path(args.preset_file)
        if given.parent == Path("."):
            candidate = Path(output_dir) / given
            if candidate.is_file():
                args.preset_file = str(candidate)
    else:
        # Auto-detect: look for <strategy>_presets.json in output_dir
        if args.sl is None or args.tp is None:
            candidate = strategy_preset_path(output_dir, strategy_name)
            if candidate.is_file():
                args.preset_file = str(candidate)


def _resolve_strategy_settings(strategy_name: str, config: dict, timeframe: str) -> dict | None:
    if strategy_name != "smc_swing":
        return None
    smc_cfg = config.get("smc", {})
    settings: dict = {}
    maps = smc_cfg.get("maps", [])
    if isinstance(maps, list) and maps:
        chosen = None
        for item in maps:
            if isinstance(item, dict) and str(item.get("ltf")) == str(timeframe):
                chosen = item
                break
        if chosen is None:
            chosen = maps[0] if isinstance(maps[0], dict) else None
        if isinstance(chosen, dict):
            settings["htf_timeframe"] = chosen.get("htf", "1h")
            settings["ltf_timeframe"] = chosen.get("ltf", timeframe)
            settings["map_id"] = chosen.get("id", f'{settings["htf_timeframe"]}_{settings["ltf_timeframe"]}')
    settings["session_filter_enabled"] = bool(smc_cfg.get("session_filter_default", True))
    if "session_windows_utc" in smc_cfg:
        settings["session_windows_utc"] = smc_cfg["session_windows_utc"]
    if "entry_modes" in smc_cfg and isinstance(smc_cfg["entry_modes"], list) and smc_cfg["entry_modes"]:
        settings["entry_mode"] = smc_cfg["entry_modes"][0]
    return settings
