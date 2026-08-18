from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel

from ..models import CandleRequest, OptimizationRequest, BacktestMetrics
from ..presets import save_best_preset, save_top_presets, strategy_preset_path
from .formatting import _resolve, generate_signals, load_candles, print_hyperopt_table, resolve_pairlist
from strategy import list_strategies

from ..hyperopt import run_optimization

_PRESET_METRIC_KEYS = frozenset({
    "net_profit_pct", "max_drawdown_pct", "win_rate_pct", "profit_factor",
    "trade_count", "equity_final", "sharpe_ratio", "calmar_ratio",
    "expectancy_pct", "avg_win_pct", "avg_loss_pct", "worst_trade_pct",
    "max_consec_losses", "sl_exit_pct", "tp_exit_pct", "signal_exit_pct",
})


def _objective_sort_key(metric: BacktestMetrics, objective: str) -> float:
    return metric.objective_value(objective)


def _objective_reverse(objective: str) -> bool:
    return objective != "max_drawdown_pct"


def _extract_metrics_payload(metric: BacktestMetrics) -> dict[str, Any]:
    return {k: v for k, v in metric.to_dict().items() if k in _PRESET_METRIC_KEYS}


def _watchdog_maybe_print(
    *,
    last_print: float,
    interval_seconds: int,
    started_at: float,
    budget_seconds: int,
    phase: str,
    pair_label: str,
    processed: int,
    total: int,
    best: BacktestMetrics | None,
) -> float:
    now = time.time()
    if now - last_print < interval_seconds:
        return last_print
    elapsed = int(now - started_at)
    remaining = max(0, budget_seconds - elapsed)
    best_label = "n/a"
    if best is not None:
        best_label = (
            f"ret={best.net_profit_pct:.2f}% dd={best.max_drawdown_pct:.2f}% "
            f"wr={best.win_rate_pct:.1f}% tr={best.trade_count}"
        )
    print(
        f"   • watchdog [{pair_label}] phase={phase} progress={processed}/{total} "
        f"elapsed={elapsed}s remaining={remaining}s best={best_label}"
    )
    return now


def _resolve_smc_config(config: dict, fallback_timeframe: str) -> dict[str, Any]:
    smc_cfg = config.get("smc", {})
    maps_raw = smc_cfg.get("maps", [])
    maps: list[dict[str, str]] = []
    if isinstance(maps_raw, list):
        for item in maps_raw:
            if not isinstance(item, dict):
                continue
            htf = str(item.get("htf", "1h"))
            ltf = str(item.get("ltf", fallback_timeframe))
            maps.append({"id": str(item.get("id", f"{htf}_{ltf}")), "htf": htf, "ltf": ltf})
    if not maps:
        maps = [{"id": f"1h_{fallback_timeframe}", "htf": "1h", "ltf": fallback_timeframe}]

    entry_modes = smc_cfg.get("entry_modes", ["both"])
    if not isinstance(entry_modes, list) or not entry_modes:
        entry_modes = ["both"]

    if smc_cfg.get("session_filter_optimize", True):
        session_modes = [True, False]
    else:
        session_modes = [bool(smc_cfg.get("session_filter_default", True))]

    return {
        "maps": maps,
        "entry_modes": [str(mode) for mode in entry_modes],
        "session_modes": session_modes,
        "session_windows_utc": smc_cfg.get("session_windows_utc", [[7, 17], [12, 22]]),
        "time_budget_minutes": int(smc_cfg.get("time_budget_minutes", 10)),
        "watchdog_seconds": int(smc_cfg.get("watchdog_seconds", 60)),
        "coarse_trials": int(smc_cfg.get("coarse_trials", 30)),
        "fine_trials": int(smc_cfg.get("fine_trials", 120)),
        "coarse_top_k": int(smc_cfg.get("coarse_top_k", 6)),
        "preset_top_n": int(smc_cfg.get("preset_top_n", 20)),
        "min_signals": int(smc_cfg.get("min_signals", 8)),
        "fine_span_ratio": float(smc_cfg.get("fine_span_ratio", 0.35)),
    }


def _run_single_hyperopt_standard(
    symbol: str,
    exchange: str,
    timeframe: str,
    session_type: str,
    adjustment: str,
    strategy_name: str,
    initial_capital: float,
    data_dir: str,
    output_dir_base: str,
    mode: str,
    start: str | None,
    end: str | None,
    sl_min: float,
    sl_max: float,
    tp_min: float,
    tp_max: float,
    objective: str,
    top_n: int,
    n_trials: int,
) -> tuple[int, tuple[float, float] | None]:
    candle_request = CandleRequest(
        symbol=symbol,
        exchange=exchange,
        timeframe=timeframe,
        start=start,
        end=end,
        session=session_type,
        adjustment=adjustment,
    )

    try:
        candles = load_candles(candle_request, data_dir, compact=True)
        if candles is None or len(candles) == 0:
            print("  Error: No candle data found. Optimization aborted.")
            return 1, None

        signal_frame, strategy = generate_signals(
            strategy_name,
            candles,
            mode,
            start,
            end,
            quiet=True,
        )
        if signal_frame is None or len(signal_frame) == 0:
            print("  Error: No signals generated. Optimization aborted.")
            return 1, None

        buy_count = int(signal_frame["buy_signal"].sum())
        sell_count = int(signal_frame["sell_signal"].sum())
        in_range_bars = int(signal_frame["in_date_range"].sum())
        density_per_1k = (buy_count + sell_count) / max(in_range_bars, 1) * 1000
        density_label = "Low" if density_per_1k < 5 else "Medium" if density_per_1k < 20 else "High"
        print(f"   • Signals : {buy_count} buy / {sell_count} sell ({density_label} density ({density_per_1k:.2f}/1k bars))")

        request = OptimizationRequest(
            candle_request=candle_request,
            mode=mode,
            objective=objective,
            sl_min=sl_min,
            sl_max=sl_max,
            tp_min=tp_min,
            tp_max=tp_max,
            top_n=top_n,
            n_trials=n_trials,
            initial_equity=initial_capital,
        )

        bundle = run_optimization(
            signal_frame=signal_frame,
            candle_request=candle_request,
            strategy=strategy,
            request=request,
            output_path=strategy_preset_path(output_dir_base, strategy_name),
            initial_equity=initial_capital,
        )

        print_hyperopt_table(bundle.results, top_n)
        if not bundle.results:
            print("  Error: Optimization produced no ranked results.")
            return 1, None

        best = bundle.results[0]
        metrics = _extract_metrics_payload(best)
        preset_path = save_best_preset(
            strategy_preset_path(output_dir_base, strategy_name),
            strategy=strategy_name,
            pair=f"{exchange}:{symbol}",
            timeframe=timeframe,
            session=session_type,
            adjustment=adjustment,
            mode=mode,
            sl=best.sl_pct,
            tp=best.tp_pct,
            objective=objective,
            search_method="bayesian",
            metrics=metrics,
        )
        Console().print(f"   [green]✔[/green] Best preset saved to: {preset_path}")
        return 0, (best.sl_pct, best.tp_pct)
    except Exception as exc:
        print(f"\n  Error: Optimization failed ({exc})")
        logging.exception("Exception during standard hyperopt for %s:%s", exchange, symbol)
        return 1, None


def _run_single_hyperopt_smc(
    *,
    symbol: str,
    exchange: str,
    session_type: str,
    adjustment: str,
    strategy_name: str,
    initial_capital: float,
    data_dir: str,
    output_dir_base: str,
    mode: str,
    start: str | None,
    end: str | None,
    sl_min: float,
    sl_max: float,
    tp_min: float,
    tp_max: float,
    objective: str,
    config: dict[str, Any],
) -> int:
    smc_cfg = _resolve_smc_config(config, fallback_timeframe=config.get("timeframe", "5m"))
    pair_label = f"{exchange}:{symbol}"
    started = time.time()
    budget_seconds = max(60, smc_cfg["time_budget_minutes"] * 60)
    watchdog_seconds = max(10, smc_cfg["watchdog_seconds"])
    coarse_trials = max(5, smc_cfg["coarse_trials"])
    fine_trials = max(10, smc_cfg["fine_trials"])
    coarse_top_k = max(1, smc_cfg["coarse_top_k"])
    preset_top_n = max(1, smc_cfg["preset_top_n"])
    min_signals = max(1, smc_cfg["min_signals"])
    fine_span_ratio = min(max(smc_cfg["fine_span_ratio"], 0.05), 0.9)

    combos: list[dict[str, Any]] = []
    for map_item in smc_cfg["maps"]:
        for entry_mode in smc_cfg["entry_modes"]:
            for session_enabled in smc_cfg["session_modes"]:
                combos.append({
                    "map_id": map_item["id"],
                    "htf": map_item["htf"],
                    "ltf": map_item["ltf"],
                    "entry_mode": entry_mode,
                    "session_filter_enabled": session_enabled,
                })

    candle_cache: dict[str, Any] = {}
    coarse_candidates: list[dict[str, Any]] = []
    best_so_far: BacktestMetrics | None = None
    last_watchdog = started

    for index, combo in enumerate(combos, start=1):
        elapsed = time.time() - started
        if elapsed >= budget_seconds:
            print(f"   • Time budget reached during coarse stage ({elapsed:.1f}s).")
            break

        timeframe = combo["ltf"]
        candles = candle_cache.get(timeframe)
        if candles is None:
            candle_request = CandleRequest(
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                start=start,
                end=end,
                session=session_type,
                adjustment=adjustment,
            )
            candles = load_candles(candle_request, data_dir, compact=True)
            candle_cache[timeframe] = candles
        if candles is None or len(candles) == 0:
            continue

        strategy_settings = {
            "htf_timeframe": combo["htf"],
            "ltf_timeframe": combo["ltf"],
            "map_id": combo["map_id"],
            "entry_mode": combo["entry_mode"],
            "session_filter_enabled": combo["session_filter_enabled"],
            "session_windows_utc": smc_cfg["session_windows_utc"],
        }
        signal_frame, strategy = generate_signals(
            strategy_name,
            candles,
            mode,
            start,
            end,
            strategy_settings=strategy_settings,
            quiet=True,
        )
        buy_count = int(signal_frame["buy_signal"].sum())
        sell_count = int(signal_frame["sell_signal"].sum())
        signal_count = buy_count + sell_count
        if signal_count < min_signals:
            last_watchdog = _watchdog_maybe_print(
                last_print=last_watchdog,
                interval_seconds=watchdog_seconds,
                started_at=started,
                budget_seconds=budget_seconds,
                phase="coarse",
                pair_label=pair_label,
                processed=index,
                total=len(combos),
                best=best_so_far,
            )
            continue

        request = OptimizationRequest(
            candle_request=CandleRequest(
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                start=start,
                end=end,
                session=session_type,
                adjustment=adjustment,
            ),
            mode=mode,
            objective=objective,
            sl_min=sl_min,
            sl_max=sl_max,
            tp_min=tp_min,
            tp_max=tp_max,
            top_n=1,
            n_trials=coarse_trials,
            initial_equity=initial_capital,
        )
        bundle = run_optimization(
            signal_frame=signal_frame,
            candle_request=request.candle_request,
            strategy=strategy,
            request=request,
            output_path=strategy_preset_path(output_dir_base, strategy_name),
            initial_equity=initial_capital,
        )
        if not bundle.results:
            continue
        best_metric = bundle.results[0]
        coarse_candidates.append({
            "combo": combo,
            "metric": best_metric,
            "timeframe": timeframe,
            "strategy_settings": strategy_settings,
            "signal_count": signal_count,
        })
        if best_so_far is None:
            best_so_far = best_metric
        else:
            current = _objective_sort_key(best_metric, objective)
            previous = _objective_sort_key(best_so_far, objective)
            if (current > previous and _objective_reverse(objective)) or (current < previous and not _objective_reverse(objective)):
                best_so_far = best_metric

        last_watchdog = _watchdog_maybe_print(
            last_print=last_watchdog,
            interval_seconds=watchdog_seconds,
            started_at=started,
            budget_seconds=budget_seconds,
            phase="coarse",
            pair_label=pair_label,
            processed=index,
            total=len(combos),
            best=best_so_far,
        )

    if not coarse_candidates:
        print("   • No viable SMC candidates produced trades in coarse stage.")
        return 1

    coarse_candidates = sorted(
        coarse_candidates,
        key=lambda item: _objective_sort_key(item["metric"], objective),
        reverse=_objective_reverse(objective),
    )[:coarse_top_k]

    final_metrics: list[tuple[BacktestMetrics, dict[str, Any], str]] = []
    for idx, candidate in enumerate(coarse_candidates, start=1):
        elapsed = time.time() - started
        if elapsed >= budget_seconds:
            print(f"   • Time budget reached during fine stage ({elapsed:.1f}s).")
            break

        combo = candidate["combo"]
        timeframe = candidate["timeframe"]
        base_metric: BacktestMetrics = candidate["metric"]
        sl_span = (sl_max - sl_min) * fine_span_ratio
        tp_span = (tp_max - tp_min) * fine_span_ratio
        fine_sl_min = max(sl_min, base_metric.sl_pct - sl_span / 2)
        fine_sl_max = min(sl_max, base_metric.sl_pct + sl_span / 2)
        fine_tp_min = max(tp_min, base_metric.tp_pct - tp_span / 2)
        fine_tp_max = min(tp_max, base_metric.tp_pct + tp_span / 2)
        if fine_sl_min >= fine_sl_max:
            fine_sl_min, fine_sl_max = sl_min, sl_max
        if fine_tp_min >= fine_tp_max:
            fine_tp_min, fine_tp_max = tp_min, tp_max

        candles = candle_cache[timeframe]
        signal_frame, strategy = generate_signals(
            strategy_name,
            candles,
            mode,
            start,
            end,
            strategy_settings=candidate["strategy_settings"],
            quiet=True,
        )
        request = OptimizationRequest(
            candle_request=CandleRequest(
                symbol=symbol,
                exchange=exchange,
                timeframe=timeframe,
                start=start,
                end=end,
                session=session_type,
                adjustment=adjustment,
            ),
            mode=mode,
            objective=objective,
            sl_min=fine_sl_min,
            sl_max=fine_sl_max,
            tp_min=fine_tp_min,
            tp_max=fine_tp_max,
            top_n=preset_top_n,
            n_trials=fine_trials,
            initial_equity=initial_capital,
        )
        bundle = run_optimization(
            signal_frame=signal_frame,
            candle_request=request.candle_request,
            strategy=strategy,
            request=request,
            output_path=strategy_preset_path(output_dir_base, strategy_name),
            initial_equity=initial_capital,
        )
        for metric in bundle.results:
            final_metrics.append((metric, combo, timeframe))

        best_candidate = bundle.results[0] if bundle.results else None
        if best_candidate is not None:
            if best_so_far is None:
                best_so_far = best_candidate
            else:
                current = _objective_sort_key(best_candidate, objective)
                previous = _objective_sort_key(best_so_far, objective)
                if (current > previous and _objective_reverse(objective)) or (current < previous and not _objective_reverse(objective)):
                    best_so_far = best_candidate

        last_watchdog = _watchdog_maybe_print(
            last_print=last_watchdog,
            interval_seconds=watchdog_seconds,
            started_at=started,
            budget_seconds=budget_seconds,
            phase="fine",
            pair_label=pair_label,
            processed=idx,
            total=len(coarse_candidates),
            best=best_so_far,
        )

    if not final_metrics:
        print("   • No final SMC metrics generated.")
        return 1

    grouped: dict[str, list[tuple[BacktestMetrics, dict[str, Any], str]]] = {}
    for entry in final_metrics:
        grouped.setdefault(entry[2], []).append(entry)

    preset_path = strategy_preset_path(output_dir_base, strategy_name)
    for timeframe, entries in grouped.items():
        dedup: dict[tuple[str, float, float], tuple[BacktestMetrics, dict[str, Any], str]] = {}
        for metric, combo, tf in entries:
            key = (combo["map_id"], round(metric.sl_pct, 2), round(metric.tp_pct, 2))
            existing = dedup.get(key)
            if existing is None:
                dedup[key] = (metric, combo, tf)
                continue
            candidate_value = _objective_sort_key(metric, objective)
            existing_value = _objective_sort_key(existing[0], objective)
            better = (candidate_value > existing_value and _objective_reverse(objective)) or (
                candidate_value < existing_value and not _objective_reverse(objective)
            )
            if better:
                dedup[key] = (metric, combo, tf)

        ranked = sorted(
            dedup.values(),
            key=lambda item: _objective_sort_key(item[0], objective),
            reverse=_objective_reverse(objective),
        )[:preset_top_n]

        preset_items: list[dict[str, Any]] = []
        for rank, (metric, combo, _) in enumerate(ranked, start=1):
            preset_items.append({
                "rank": rank,
                "sl": metric.sl_pct,
                "tp": metric.tp_pct,
                "map_id": combo["map_id"],
                "metrics": _extract_metrics_payload(metric),
                "meta": {
                    "htf": combo["htf"],
                    "ltf": combo["ltf"],
                    "entry_mode": combo["entry_mode"],
                    "session_filter_enabled": combo["session_filter_enabled"],
                },
            })

        save_top_presets(
            preset_path,
            strategy=strategy_name,
            pair=pair_label,
            timeframe=timeframe,
            session=session_type,
            adjustment=adjustment,
            mode=mode,
            objective=objective,
            search_method="coarse_to_fine",
            items=preset_items,
        )

    if best_so_far is not None:
        Console().print(
            f"   [green]✔[/green] Saved SMC Top-{preset_top_n} presets to: {preset_path} "
            f"(best: SL={best_so_far.sl_pct:.2f}, TP={best_so_far.tp_pct:.2f}, "
            f"ret={best_so_far.net_profit_pct:.2f}%)"
        )
    return 0


def run_hyperopt(args: argparse.Namespace, config: dict) -> int:
    strategy_name = _resolve(args, config, "strategy")
    available_strategies = list_strategies()

    if not strategy_name or strategy_name not in available_strategies:
        print("Error: Invalid or no strategy specified.")
        print(f"Available strategies: {', '.join(available_strategies) or '(none)'}")
        return 1

    timeframe = _resolve(args, config, "timeframe")
    session_type = _resolve(args, config, "session")
    mode = _resolve(args, config, "mode", "long")
    adjustment = args.adjustment
    initial_capital = config.get("initial_capital", 1000.0)
    data_dir = config.get("data_dir", "./data")

    output_dir_base = config.get("output_dir", "./outputs")
    Path(output_dir_base).mkdir(parents=True, exist_ok=True)

    opt_cfg = config.get("optimization", {})
    sl_range = opt_cfg.get("sl_range", {})
    tp_range = opt_cfg.get("tp_range", {})

    sl_min = args.sl_min if args.sl_min is not None else sl_range.get("min", 0.5)
    sl_max = args.sl_max if args.sl_max is not None else sl_range.get("max", 5.0)
    tp_min = args.tp_min if args.tp_min is not None else tp_range.get("min", 1.0)
    tp_max = args.tp_max if args.tp_max is not None else tp_range.get("max", 10.0)

    objective = args.objective or opt_cfg.get("objective", "net_profit_pct")
    top_n = args.top_n if args.top_n is not None else opt_cfg.get("top_n", 5)
    n_trials = args.n_trials if args.n_trials is not None else opt_cfg.get("n_trials", 100)

    symbols = resolve_pairlist(args, config)
    if not symbols:
        print("Error: No trading pairs resolved. Please check your config or arguments.")
        return 1

    console = Console()
    header_text = (
        f"⚙ HYPERVIEW - BATCH HYPER-OPTIMIZATION\n"
        f"  Strategy : {strategy_name} | Mode: {mode} | Timeframe: {timeframe}\n"
        f"  Targets  : {len(symbols)} pair(s)"
    )
    console.print()
    console.print(Panel(header_text, expand=True))

    rc = 0
    for index, (symbol, pair_exchange) in enumerate(symbols, start=1):
        line = "─" * 72
        console.print(f"\n 📊 [{index}/{len(symbols)}] {pair_exchange}:{symbol}")
        console.print(f" {line}")

        if strategy_name == "smc_swing":
            pair_rc = _run_single_hyperopt_smc(
                symbol=symbol,
                exchange=pair_exchange,
                session_type=session_type,
                adjustment=adjustment,
                strategy_name=strategy_name,
                initial_capital=initial_capital,
                data_dir=data_dir,
                output_dir_base=output_dir_base,
                mode=mode,
                start=args.start,
                end=args.end,
                sl_min=sl_min,
                sl_max=sl_max,
                tp_min=tp_min,
                tp_max=tp_max,
                objective=objective,
                config=config,
            )
            if pair_rc != 0:
                rc = 1
            continue

        pair_rc, _ = _run_single_hyperopt_standard(
            symbol=symbol,
            exchange=pair_exchange,
            timeframe=timeframe,
            session_type=session_type,
            adjustment=adjustment,
            strategy_name=strategy_name,
            initial_capital=initial_capital,
            data_dir=data_dir,
            output_dir_base=output_dir_base,
            mode=mode,
            start=args.start,
            end=args.end,
            sl_min=sl_min,
            sl_max=sl_max,
            tp_min=tp_min,
            tp_max=tp_max,
            objective=objective,
            top_n=top_n,
            n_trials=n_trials,
        )
        if pair_rc != 0:
            rc = 1

    return rc
