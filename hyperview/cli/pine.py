from __future__ import annotations

import argparse
from pathlib import Path
import json
from typing import Any

from ..models import CandleRequest, Objective
from ..presets import save_top_presets, strategy_preset_path
from ..pine.analytics import (
    analyze_best_when,
    context_payload_from_candidates,
    load_context_payload,
    write_analysis_reports,
)
from ..pine.exporter import (
    build_metric_filename,
    default_filename_template,
    render_optimized_pine,
    resolve_optimization_report_dir,
    sanitize_token,
    utc_run_id,
)
from ..pine.inputs import extract_pine_inputs, resolve_search_dimensions
from ..pine.optimizer import (
    PineCandidate,
    deserialize_candidate,
    evaluate_with_backtester,
    run_two_stage_optimization,
    serialize_candidate,
)
from .formatting import _resolve, generate_signals, load_candles, resolve_pairlist

def run_pine_optimize(args: argparse.Namespace, config: dict[str, Any]) -> int:
    pine_path = Path(args.pine_file)
    if not pine_path.is_file():
        print(f"Error: Pine file not found: {pine_path}")
        return 1
    pine_text = pine_path.read_text(encoding="utf-8")
    specs = extract_pine_inputs(pine_text)
    dimensions, warnings = resolve_search_dimensions(specs)
    if not dimensions:
        print("Error: No optimizable inputs found in Pine file.")
        return 1
    for warning in warnings:
        print(f"   • warning: {warning}")

    timeframe = _resolve(args, config, "timeframe")
    session = _resolve(args, config, "session")
    mode = _resolve(args, config, "mode", "long")
    strategy_name = _resolve(args, config, "strategy", "smc_swing")
    adjustment = args.adjustment
    data_dir = config.get("data_dir", "./data")
    output_dir = config.get("output_dir", "./results")
    initial_capital = float(config.get("initial_capital", 100_000.0))
    objective: Objective = args.objective or config.get("optimization", {}).get("objective", "net_profit_pct")
    min_trades = int(args.min_trades or config.get("smc", {}).get("min_signals", 8))
    min_signals = int(args.min_signals or config.get("smc", {}).get("min_signals", 8))
    coarse_trials = int(args.coarse_trials or config.get("smc", {}).get("coarse_trials", 30))
    fine_trials = int(args.fine_trials or config.get("smc", {}).get("fine_trials", 120))
    coarse_top_k = int(args.coarse_top_k or config.get("smc", {}).get("coarse_top_k", 6))
    preset_top_n = int(args.preset_top_n or config.get("smc", {}).get("preset_top_n", 20))
    watchdog_seconds = int(args.watchdog_seconds or config.get("smc", {}).get("watchdog_seconds", 60))
    budget_seconds = int((args.budget_minutes or config.get("smc", {}).get("time_budget_minutes", 10)) * 60)
    fine_span_ratio = float(args.fine_span_ratio or config.get("smc", {}).get("fine_span_ratio", 0.35))
    sl_pct = float(args.sl if args.sl is not None else config.get("optimization", {}).get("sl_range", {}).get("min", 1.0))
    tp_pct = float(args.tp if args.tp is not None else config.get("optimization", {}).get("tp_range", {}).get("min", 2.0))
    emit_optimized_pine = bool(args.emit_optimized_pine)
    optimized_dir = Path(args.optimized_dir or "strategies/optimized")
    filename_template = args.filename_template or default_filename_template()
    strategy_slug = pine_path.stem
    run_id = utc_run_id()

    pairs = resolve_pairlist(args, config)
    if not pairs:
        print("Error: No trading pairs resolved.")
        return 1

    all_ranked: list[PineCandidate] = []
    grouped: dict[tuple[str, str], list[PineCandidate]] = {}
    for symbol, exchange in pairs:
        pair_label = f"{exchange}:{symbol}"
        candle_request = CandleRequest(
            symbol=symbol,
            exchange=exchange,
            timeframe=timeframe,
            start=args.start,
            end=args.end,
            session=session,
            adjustment=adjustment,
        )
        candles = load_candles(candle_request, data_dir, compact=True)
        if candles is None or len(candles) == 0:
            print(f"   • skip {pair_label}: no candles")
            continue

        def _signal_frame_factory(settings: dict[str, Any]):
            signal_frame, _ = generate_signals(
                strategy_name,
                candles,
                mode,
                args.start,
                args.end,
                strategy_settings=settings,
                quiet=True,
            )
            return signal_frame

        def _evaluate(params: dict[str, Any], *, min_trades: int, min_signals: int):
            return evaluate_with_backtester(
                params=params,
                pair=pair_label,
                timeframe=timeframe,
                mode=mode,
                sl_pct=sl_pct,
                tp_pct=tp_pct,
                candle_request=candle_request,
                signal_frame_factory=_signal_frame_factory,
                min_trades=min_trades,
                min_signals=min_signals,
            )

        ranked = run_two_stage_optimization(
            dimensions=dimensions,
            objective=objective,
            coarse_trials=coarse_trials,
            fine_trials=fine_trials,
            coarse_top_k=coarse_top_k,
            min_trades=min_trades,
            min_signals=min_signals,
            fine_span_ratio=fine_span_ratio,
            time_budget_seconds=budget_seconds,
            watchdog_seconds=watchdog_seconds,
            evaluate_candidate=_evaluate,
        )
        if not ranked:
            print(f"   • skip {pair_label}: no viable candidate")
            continue
        grouped[(pair_label, timeframe)] = ranked
        all_ranked.extend(ranked)

    if not all_ranked:
        print("Error: No ranked candidates produced.")
        return 1

    preset_path = Path(args.preset_file) if args.preset_file else strategy_preset_path(output_dir, strategy_name)
    exported_files: list[Path] = []
    for (pair, tf), items in grouped.items():
        reverse = objective != "max_drawdown_pct"
        items = sorted(items, key=lambda item: item.metrics.objective_value(objective), reverse=reverse)
        top_items = items[:preset_top_n]
        preset_items: list[dict[str, Any]] = []
        for rank, candidate in enumerate(top_items, start=1):
            preset_items.append(
                {
                    "rank": rank,
                    "sl": candidate.metrics.sl_pct,
                    "tp": candidate.metrics.tp_pct,
                    "map_id": candidate.map_id,
                    "session_window": candidate.session_window,
                    "analysis_tags": candidate.analysis_tags,
                    "min_trades_gate": min_trades,
                    "metrics": candidate.metrics.to_dict(),
                    "meta": {
                        "params": candidate.params,
                        "settings": candidate.settings,
                    },
                }
            )
        pair_exchange, pair_symbol = pair.split(":", 1)
        save_top_presets(
            preset_path,
            strategy=strategy_name,
            pair=pair,
            timeframe=tf,
            session=session,
            adjustment=adjustment,
            mode=mode,
            objective=objective,
            search_method="coarse_to_fine",
            items=preset_items,
        )
        print(f"   • saved top-{len(top_items)} presets for {pair_exchange}:{pair_symbol}")

        report_dir = resolve_optimization_report_dir(
            output_dir=output_dir,
            pair=pair,
            timeframe=tf,
            explicit_report_dir=args.report_dir,
        )
        context_payload = context_payload_from_candidates(
            candidates=top_items,
            pine_file=str(pine_path),
            preset_file=str(preset_path),
            min_trades=min_trades,
            initial_capital=initial_capital,
        )
        context_payload["run_id"] = run_id
        analytics_payload = analyze_best_when(top_items, min_trades=min_trades)
        paths = write_analysis_reports(output_dir=report_dir, context_payload=context_payload, analytics_payload=analytics_payload)
        context_path = report_dir / "pine_optimize_context.json"
        context_path.write_text(json.dumps(context_payload, indent=2) + "\n", encoding="utf-8")
        top_path = report_dir / "top_candidates.json"
        top_payload = {
            "run_id": run_id,
            "pair": pair,
            "timeframe": tf,
            "objective": objective,
            "items": [serialize_candidate(candidate) for candidate in top_items],
        }
        top_path.write_text(json.dumps(top_payload, indent=2) + "\n", encoding="utf-8")

        print(f"✔ Context: {context_path}")
        print(f"✔ Report : {paths['json']}")
        print(f"✔ Report VI: {paths['md_vi']}")
        print(f"✔ Top-N : {top_path}")

        if emit_optimized_pine and top_items:
            best = top_items[0]
            optimized_dir.mkdir(parents=True, exist_ok=True)
            filename = build_metric_filename(
                template=filename_template,
                pair=pair,
                timeframe=tf,
                strategy_name=strategy_slug,
                candidate=best,
            )
            optimized_path = optimized_dir / filename
            optimized_source = render_optimized_pine(
                source_text=pine_text,
                candidate=best,
                source_file=str(pine_path),
                start=args.start,
                end=args.end,
                run_id=run_id,
            )
            optimized_path.write_text(optimized_source, encoding="utf-8")
            exported_files.append(optimized_path)
            print(f"✔ Optimized Pine: {optimized_path}")

    print(f"✔ Presets: {preset_path}")
    if exported_files:
        print(f"✔ Optimized files exported: {len(exported_files)}")
    return 0


def run_pine_batch_optimize(args: argparse.Namespace, config: dict[str, Any]) -> int:
    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        print(f"Error: Input directory not found: {input_dir}")
        return 1

    pine_files = sorted(input_dir.glob("*.pine"))
    if not pine_files:
        print(f"Error: No .pine files found in {input_dir}")
        return 1

    output_dir = config.get("output_dir", "./results")
    report_root = Path(args.report_root) if args.report_root else Path(output_dir) / "optimizations"
    timeframes = args.timeframes or [str(_resolve(args, config, "timeframe"))]
    symbols = args.symbols or [f"{exchange}:{symbol}" for symbol, exchange in resolve_pairlist(args, config)]
    if not symbols:
        print("Error: No symbols resolved for batch optimization.")
        return 1

    leaderboard_rows: list[dict[str, Any]] = []
    failures = 0
    for pine_file in pine_files:
        strategy_slug = sanitize_token(pine_file.stem)
        for symbol in symbols:
            for timeframe in timeframes:
                symbol_slug = sanitize_token(symbol.split(":", 1)[-1])
                run_report_dir = report_root / symbol_slug / timeframe.lower() / strategy_slug
                one_args = argparse.Namespace(
                    pine_file=str(pine_file),
                    symbol=symbol,
                    timeframe=timeframe,
                    start=args.start,
                    end=args.end,
                    session=args.session,
                    adjustment=args.adjustment,
                    strategy=args.strategy,
                    mode=args.mode,
                    objective=args.objective,
                    coarse_trials=args.coarse_trials,
                    fine_trials=args.fine_trials,
                    coarse_top_k=args.coarse_top_k,
                    preset_top_n=args.preset_top_n,
                    min_trades=args.min_trades,
                    min_signals=args.min_signals,
                    budget_minutes=args.budget_minutes,
                    watchdog_seconds=args.watchdog_seconds,
                    fine_span_ratio=args.fine_span_ratio,
                    sl=args.sl,
                    tp=args.tp,
                    preset_file=args.preset_file,
                    report_dir=str(run_report_dir),
                    emit_optimized_pine=args.emit_optimized_pine,
                    optimized_dir=args.optimized_dir,
                    filename_template=args.filename_template,
                )
                print(f"== batch optimize: pine={pine_file.name} symbol={symbol} timeframe={timeframe}")
                rc = run_pine_optimize(one_args, config)
                if rc != 0:
                    failures += 1
                    continue
                context_path = run_report_dir / "pine_optimize_context.json"
                if not context_path.is_file():
                    continue
                payload = load_context_payload(context_path)
                candidates = payload.get("candidates", [])
                if not candidates:
                    continue
                best = candidates[0]
                metrics = best.get("metrics", {})
                leaderboard_rows.append(
                    {
                        "strategy": strategy_slug,
                        "symbol": symbol,
                        "timeframe": timeframe,
                        "net_profit_pct": metrics.get("net_profit_pct", 0.0),
                        "max_drawdown_pct": metrics.get("max_drawdown_pct", 0.0),
                        "profit_factor": metrics.get("profit_factor", 0.0),
                        "trade_count": metrics.get("trade_count", 0),
                        "context_file": str(context_path),
                    }
                )

    leaderboard_rows.sort(key=lambda item: float(item.get("net_profit_pct", 0.0)), reverse=True)
    report_root.mkdir(parents=True, exist_ok=True)
    summary_path = report_root / "leaderboard.json"
    summary_path.write_text(json.dumps({"items": leaderboard_rows}, indent=2) + "\n", encoding="utf-8")
    markdown_path = report_root / "leaderboard.md"
    markdown_path.write_text(_render_batch_markdown(leaderboard_rows), encoding="utf-8")
    print(f"✔ Batch leaderboard JSON: {summary_path}")
    print(f"✔ Batch leaderboard MD  : {markdown_path}")
    if failures:
        print(f"⚠ Batch completed with failures: {failures}")
        return 1
    return 0


def run_pine_analyze_best_when(args: argparse.Namespace, config: dict[str, Any]) -> int:
    output_dir = config.get("output_dir", "./results")
    context_path = Path(args.context_file) if args.context_file else _infer_context_path(args.preset_file, output_dir)
    if not context_path.is_file():
        print(f"Error: Context file not found: {context_path}")
        return 1
    payload = load_context_payload(context_path)
    candidates = [deserialize_candidate(item) for item in payload.get("candidates", [])]
    min_trades = int(args.min_trades or payload.get("min_trades_gate", 8))
    analytics_payload = analyze_best_when(candidates, min_trades=min_trades)
    report_dir = Path(args.report_dir) if args.report_dir else context_path.parent
    paths = write_analysis_reports(output_dir=report_dir, context_payload=payload, analytics_payload=analytics_payload)
    print(f"✔ Re-analysis complete: {paths['json']}")
    print(f"✔ Re-analysis VI report: {paths['md_vi']}")
    return 0

def _infer_context_path(preset_file: str | None, output_dir: str) -> Path:
    if preset_file:
        preset_path = Path(preset_file)
        candidate = preset_path.with_name("pine_optimize_context.json")
        if candidate.is_file():
            return candidate
    return Path(output_dir) / "pine_reports" / "pine_optimize_context.json"


def _render_batch_markdown(rows: list[dict[str, Any]]) -> str:
    lines = ["# Pine Batch Optimize Leaderboard", ""]
    if not rows:
        lines.append("_No successful optimization runs._")
        lines.append("")
        return "\n".join(lines)
    lines.append("| rank | strategy | symbol | tf | np% | dd% | pf | trades | context |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for index, row in enumerate(rows, start=1):
        lines.append(
            "| "
            + " | ".join(
                [
                    str(index),
                    str(row.get("strategy", "")),
                    str(row.get("symbol", "")),
                    str(row.get("timeframe", "")),
                    f"{float(row.get('net_profit_pct', 0.0)):.2f}",
                    f"{float(row.get('max_drawdown_pct', 0.0)):.2f}",
                    f"{float(row.get('profit_factor', 0.0)):.2f}",
                    str(int(row.get("trade_count", 0))),
                    str(row.get("context_file", "")),
                ]
            )
            + " |"
        )
    lines.append("")
    return "\n".join(lines)
