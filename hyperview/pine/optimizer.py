from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import random
import time
from typing import Any

from ..backtest.engine import TradingViewLikeBacktester
from ..models import BacktestMetrics, CandleRequest, Objective, RiskParameters, Trade
from .inputs import SearchDimension

@dataclass
class PineCandidate:
    pair: str
    timeframe: str
    params: dict[str, Any]
    settings: dict[str, Any]
    metrics: BacktestMetrics
    trades: list[Trade]
    map_id: str
    session_window: str
    analysis_tags: list[str]

def run_two_stage_optimization(
    *,
    dimensions: list[SearchDimension],
    objective: Objective,
    coarse_trials: int,
    fine_trials: int,
    coarse_top_k: int,
    min_trades: int,
    min_signals: int,
    fine_span_ratio: float,
    time_budget_seconds: int,
    watchdog_seconds: int,
    evaluate_candidate,
) -> list[PineCandidate]:
    rng = random.Random(42)
    started = time.time()
    last_watchdog = started
    accepted: list[PineCandidate] = []
    coarse: list[PineCandidate] = []

    for idx in range(1, coarse_trials + 1):
        if time.time() - started >= time_budget_seconds:
            break
        params = _sample_random_params(dimensions, rng)
        candidate = evaluate_candidate(params, min_trades=min_trades, min_signals=min_signals)
        if candidate is not None:
            coarse.append(candidate)
            accepted.append(candidate)
        last_watchdog = _watchdog(
            last_watchdog=last_watchdog,
            watchdog_seconds=watchdog_seconds,
            started=started,
            budget=time_budget_seconds,
            stage="coarse",
            progress=idx,
            total=coarse_trials,
            objective=objective,
            candidates=accepted,
        )
    if not coarse:
        return []

    seeds = _rank_candidates(coarse, objective)[: max(1, coarse_top_k)]
    per_seed = max(1, fine_trials // max(1, len(seeds)))
    for seed_idx, seed in enumerate(seeds, start=1):
        for run_idx in range(1, per_seed + 1):
            if time.time() - started >= time_budget_seconds:
                break
            params = _sample_fine_params(dimensions, seed.params, fine_span_ratio, rng)
            candidate = evaluate_candidate(params, min_trades=min_trades, min_signals=min_signals)
            if candidate is not None:
                accepted.append(candidate)
            last_watchdog = _watchdog(
                last_watchdog=last_watchdog,
                watchdog_seconds=watchdog_seconds,
                started=started,
                budget=time_budget_seconds,
                stage=f"fine-{seed_idx}",
                progress=run_idx,
                total=per_seed,
                objective=objective,
                candidates=accepted,
            )
    return _rank_candidates(accepted, objective)

def candidate_context_from_params(params: dict[str, Any], fallback_ltf: str) -> tuple[dict[str, Any], str, str, list[str]]:
    htf_raw = str(params.get("htfTf", "60"))
    htf = _normalize_timeframe(htf_raw)
    ltf = _normalize_timeframe(str(params.get("ltfTf", fallback_ltf)))
    session_a = str(params.get("sessionA", "0700-1700"))
    session_b = str(params.get("sessionB", "1200-2200"))
    map_id = f"{htf}_{ltf}".replace(" ", "")
    session_window = f"{session_a}|{session_b}"
    settings = {
        "htf_timeframe": htf,
        "ltf_timeframe": ltf,
        "map_id": map_id,
        "entry_mode": str(params.get("entryMode", "both")),
        "htf_swing_lookback": int(params.get("sweepLookback", 6)),
        "choch_lookback": int(params.get("chochLookback", 8)),
        "confirm_window_bars": int(params.get("confirmBars", 24)),
        "ob_lookback_bars": int(params.get("obLookback", 20)),
        "retest_window_bars": int(params.get("retestWindow", 12)),
        "atr_length": int(params.get("atrLength", 14)),
        "sl_buffer_atr": float(params.get("slBufferAtr", 0.25)),
        "rr_target": float(params.get("rrTarget", 2.0)),
        "session_filter_enabled": bool(params.get("sessionFilter", True)),
        "session_windows_utc": [_session_to_utc_hour_window(session_a), _session_to_utc_hour_window(session_b)],
    }
    tags = [f"entry:{settings['entry_mode']}", f"session_filter:{settings['session_filter_enabled']}"]
    return settings, map_id, session_window, tags

def serialize_candidate(candidate: PineCandidate) -> dict[str, Any]:
    return {
        "pair": candidate.pair,
        "timeframe": candidate.timeframe,
        "params": candidate.params,
        "settings": candidate.settings,
        "metrics": candidate.metrics.to_dict(),
        "map_id": candidate.map_id,
        "session_window": candidate.session_window,
        "analysis_tags": candidate.analysis_tags,
        "trades": [trade.to_dict() for trade in candidate.trades],
    }

def deserialize_candidate(payload: dict[str, Any]) -> PineCandidate:
    metrics_data = payload.get("metrics", {})
    metrics = BacktestMetrics(**metrics_data)
    trades = [Trade(**item) for item in payload.get("trades", [])]
    return PineCandidate(
        pair=str(payload.get("pair", "")),
        timeframe=str(payload.get("timeframe", "")),
        params=dict(payload.get("params", {})),
        settings=dict(payload.get("settings", {})),
        metrics=metrics,
        trades=trades,
        map_id=str(payload.get("map_id", "")),
        session_window=str(payload.get("session_window", "")),
        analysis_tags=list(payload.get("analysis_tags", [])),
    )

def evaluate_with_backtester(
    *,
    params: dict[str, Any],
    pair: str,
    timeframe: str,
    mode: str,
    sl_pct: float,
    tp_pct: float,
    candle_request: CandleRequest,
    signal_frame_factory,
    min_trades: int,
    min_signals: int,
) -> PineCandidate | None:
    settings, map_id, session_window, tags = candidate_context_from_params(params, timeframe)
    signal_frame = signal_frame_factory(settings)
    signal_count = int(signal_frame["buy_signal"].sum()) + int(signal_frame["sell_signal"].sum())
    if signal_count < min_signals:
        return None

    backtester = TradingViewLikeBacktester(candle_request=candle_request, initial_equity=100_000.0)
    risk = RiskParameters.from_mode(mode, sl_pct, tp_pct)
    result = backtester.run(signal_frame, risk, mode)  # dynamic SL/TP from strategy is applied when available
    if result.metrics.trade_count < min_trades:
        return None
    if result.metrics.expectancy_pct < -1.0:
        return None
    return PineCandidate(
        pair=pair,
        timeframe=timeframe,
        params=params,
        settings=settings,
        metrics=result.metrics,
        trades=result.trades,
        map_id=map_id,
        session_window=session_window,
        analysis_tags=tags,
    )

def _sample_random_params(dimensions: list[SearchDimension], rng: random.Random) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for dim in dimensions:
        if dim.dim_type == "categorical":
            values = dim.values or [dim.default]
            output[dim.name] = values[rng.randrange(len(values))]
            continue
        if dim.dim_type == "int":
            low = int(dim.minval if dim.minval is not None else dim.default)
            high = int(dim.maxval if dim.maxval is not None else dim.default)
            step = int(dim.step if dim.step is not None else 1)
            count = max(1, ((high - low) // max(1, step)) + 1)
            output[dim.name] = low + step * rng.randrange(count)
            continue
        low = float(dim.minval if dim.minval is not None else dim.default)
        high = float(dim.maxval if dim.maxval is not None else dim.default)
        step = float(dim.step if dim.step is not None else 0.05)
        if high <= low:
            output[dim.name] = round(low, 4)
            continue
        units = int((high - low) / step)
        output[dim.name] = round(low + step * rng.randrange(max(1, units + 1)), 6)
    return output

def _sample_fine_params(
    dimensions: list[SearchDimension],
    seed: dict[str, Any],
    fine_span_ratio: float,
    rng: random.Random,
) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for dim in dimensions:
        if dim.dim_type == "categorical":
            values = dim.values or [dim.default]
            if rng.random() < 0.8 and seed.get(dim.name) in values:
                output[dim.name] = seed.get(dim.name)
            else:
                output[dim.name] = values[rng.randrange(len(values))]
            continue
        base = seed.get(dim.name, dim.default)
        low_bound = float(dim.minval if dim.minval is not None else base)
        high_bound = float(dim.maxval if dim.maxval is not None else base)
        span = max(0.0, high_bound - low_bound)
        local_span = span * max(0.01, min(1.0, fine_span_ratio))
        local_low = max(low_bound, float(base) - local_span / 2)
        local_high = min(high_bound, float(base) + local_span / 2)
        step = float(dim.step if dim.step is not None else (1 if dim.dim_type == "int" else 0.05))
        if local_high <= local_low:
            sampled = local_low
        else:
            units = int((local_high - local_low) / max(step, 1e-9))
            sampled = local_low + max(step, 1e-9) * rng.randrange(max(1, units + 1))
        if dim.dim_type == "int":
            output[dim.name] = int(round(sampled))
        else:
            output[dim.name] = round(sampled, 6)
    return output

def _rank_candidates(candidates: list[PineCandidate], objective: Objective) -> list[PineCandidate]:
    reverse = objective != "max_drawdown_pct"
    unique: dict[tuple[str, str, str, float, float], PineCandidate] = {}
    for candidate in candidates:
        key = (
            candidate.pair,
            candidate.map_id,
            candidate.session_window,
            round(candidate.metrics.sl_pct, 4),
            round(candidate.metrics.tp_pct, 4),
        )
        existing = unique.get(key)
        if existing is None:
            unique[key] = candidate
            continue
        current = candidate.metrics.objective_value(objective)
        previous = existing.metrics.objective_value(objective)
        better = current < previous if objective == "max_drawdown_pct" else current > previous
        if better:
            unique[key] = candidate
    return sorted(unique.values(), key=lambda item: item.metrics.objective_value(objective), reverse=reverse)

def _watchdog(
    *,
    last_watchdog: float,
    watchdog_seconds: int,
    started: float,
    budget: int,
    stage: str,
    progress: int,
    total: int,
    objective: Objective,
    candidates: list[PineCandidate],
) -> float:
    now = time.time()
    if now - last_watchdog < watchdog_seconds:
        return last_watchdog
    elapsed = int(now - started)
    remaining = max(0, budget - elapsed)
    if candidates:
        best = _rank_candidates(candidates, objective)[0]
        label = (
            f"best={best.metrics.net_profit_pct:.2f}% dd={best.metrics.max_drawdown_pct:.2f}% "
            f"exp={best.metrics.expectancy_pct:.2f}% trades={best.metrics.trade_count}"
        )
    else:
        label = "best=n/a"
    print(f"   • watchdog stage={stage} progress={progress}/{total} elapsed={elapsed}s remaining={remaining}s {label}")
    return now

def _normalize_timeframe(value: str) -> str:
    text = value.strip().upper()
    if text.endswith("H") or text.endswith("D") or text.endswith("W") or text.endswith("M"):
        return text.lower()
    if text.isdigit():
        minutes = int(text)
        if minutes % 60 == 0:
            return f"{minutes // 60}h"
        return f"{minutes}m"
    return text.lower()

def _session_to_utc_hour_window(value: str) -> list[int]:
    if not value or "-" not in value:
        return [7, 17]
    start_raw, end_raw = value.split("-", 1)
    try:
        start = int(start_raw[:2])
        end = int(end_raw[:2])
    except ValueError:
        return [7, 17]
    return [start % 24, end % 24]

def utc_iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
