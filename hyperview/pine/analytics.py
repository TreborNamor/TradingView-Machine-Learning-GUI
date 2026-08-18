from __future__ import annotations

from collections import defaultdict
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from .optimizer import PineCandidate, serialize_candidate

def analyze_best_when(candidates: list[PineCandidate], *, min_trades: int) -> dict[str, Any]:
    by_session_hour: dict[tuple[int, str], list[float]] = defaultdict(list)
    by_month_quarter: dict[tuple[str, str], list[float]] = defaultdict(list)
    by_map_hour: dict[tuple[str, int], list[float]] = defaultdict(list)

    for candidate in candidates:
        for trade in candidate.trades:
            dt = datetime.fromtimestamp(int(trade.exit_time), tz=timezone.utc)
            hour = dt.hour
            month = dt.strftime("%Y-%m")
            quarter = f"{dt.year}-Q{((dt.month - 1) // 3) + 1}"
            session_label = _session_label(hour)
            by_session_hour[(hour, session_label)].append(float(trade.return_pct))
            by_month_quarter[(month, quarter)].append(float(trade.return_pct))
            by_map_hour[(candidate.map_id, hour)].append(float(trade.return_pct))

    return {
        "min_trades_gate": min_trades,
        "best_by_session_hour": _rank_buckets(by_session_hour, min_trades=min_trades, key_names=("hour_utc", "session")),
        "best_by_month_quarter": _rank_buckets(by_month_quarter, min_trades=min_trades, key_names=("month", "quarter")),
        "best_by_map_hour": _rank_buckets(by_map_hour, min_trades=min_trades, key_names=("map_id", "hour_utc")),
    }

def write_analysis_reports(
    *,
    output_dir: str | Path,
    context_payload: dict[str, Any],
    analytics_payload: dict[str, Any],
) -> dict[str, str]:
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "best_when_report.json"
    md_path = out_dir / "best_when_report.md"
    csv_session_path = out_dir / "best_by_session_hour.csv"
    csv_month_path = out_dir / "best_by_month_quarter.csv"
    csv_map_hour_path = out_dir / "best_by_map_hour.csv"

    bundle = {
        "context": context_payload,
        "analysis": analytics_payload,
    }
    json_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(analytics_payload), encoding="utf-8")
    _write_csv(csv_session_path, analytics_payload["best_by_session_hour"])
    _write_csv(csv_month_path, analytics_payload["best_by_month_quarter"])
    _write_csv(csv_map_hour_path, analytics_payload["best_by_map_hour"])
    vi_summary_path = out_dir / "README_best_result_vi.md"
    vi_summary_path.write_text(_render_vietnamese_summary(context_payload, analytics_payload), encoding="utf-8")
    return {
        "json": str(json_path),
        "md": str(md_path),
        "csv_session_hour": str(csv_session_path),
        "csv_month_quarter": str(csv_month_path),
        "csv_map_hour": str(csv_map_hour_path),
        "md_vi": str(vi_summary_path),
    }

def context_payload_from_candidates(
    *,
    candidates: list[PineCandidate],
    pine_file: str,
    preset_file: str,
    min_trades: int,
    initial_capital: float = 100_000.0,
) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "pine_file": pine_file,
        "preset_file": preset_file,
        "min_trades_gate": min_trades,
        "initial_capital": float(initial_capital),
        "candidate_count": len(candidates),
        "candidates": [serialize_candidate(candidate) for candidate in candidates],
    }

def load_context_payload(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def _rank_buckets(
    buckets: dict[tuple[Any, ...], list[float]],
    *,
    min_trades: int,
    key_names: tuple[str, ...],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for key, returns in buckets.items():
        if len(returns) < min_trades:
            continue
        stats = _bucket_metrics(returns)
        row: dict[str, Any] = dict(zip(key_names, key))
        row.update(stats)
        rows.append(row)
    rows.sort(key=lambda item: (item["net_profit_pct"], item["expectancy_pct"]), reverse=True)
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
    return rows

def _bucket_metrics(returns: list[float]) -> dict[str, float | int]:
    net = float(sum(returns))
    trade_count = len(returns)
    expectancy = net / trade_count if trade_count else 0.0
    max_dd = _drawdown_from_returns(returns)
    calmar = net / max_dd if max_dd > 0 else 0.0
    return {
        "net_profit_pct": round(net, 4),
        "expectancy_pct": round(expectancy, 4),
        "calmar_ratio": round(calmar, 4),
        "max_drawdown_pct": round(max_dd, 4),
        "trade_count": trade_count,
    }

def _drawdown_from_returns(returns: list[float]) -> float:
    equity = 100.0
    peak = equity
    max_dd = 0.0
    for value in returns:
        equity *= 1.0 + value / 100.0
        if equity > peak:
            peak = equity
        if peak > 0:
            dd = ((peak - equity) / peak) * 100.0
            if dd > max_dd:
                max_dd = dd
    return max_dd

def _session_label(hour_utc: int) -> str:
    if 12 <= hour_utc < 17:
        return "London+NY Overlap"
    if 7 <= hour_utc < 12:
        return "London"
    if 17 <= hour_utc < 22:
        return "New York"
    return "Off Session"

def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def _render_markdown(analysis: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# Best-When Analysis")
    lines.append("")
    lines.append(f"- Min trades gate: `{analysis.get('min_trades_gate', 0)}`")
    lines.append("")
    lines.extend(_render_table("Best By Session Hour", analysis.get("best_by_session_hour", [])))
    lines.append("")
    lines.extend(_render_table("Best By Month Quarter", analysis.get("best_by_month_quarter", [])))
    lines.append("")
    lines.extend(_render_table("Best By Map Hour", analysis.get("best_by_map_hour", [])))
    lines.append("")
    return "\n".join(lines)

def _render_table(title: str, rows: list[dict[str, Any]]) -> list[str]:
    output = [f"## {title}"]
    if not rows:
        output.append("")
        output.append("_No rows matched the min-trades gate._")
        return output
    keys = list(rows[0].keys())
    output.append("")
    output.append("| " + " | ".join(keys) + " |")
    output.append("| " + " | ".join(["---"] * len(keys)) + " |")
    for row in rows[:20]:
        output.append("| " + " | ".join(str(row[key]) for key in keys) + " |")
    return output

def _render_vietnamese_summary(context: dict[str, Any], analysis: dict[str, Any]) -> str:
    candidates = context.get("candidates", [])
    if not candidates:
        return "# Báo Cáo Kết Quả Pine Optimize (Tiếng Việt)\n\nKhông có candidate để tổng hợp.\n"
    best = candidates[0]
    metrics = best.get("metrics", {})
    params = best.get("params", {})
    initial_capital = float(context.get("initial_capital", 100_000.0))
    final_equity = float(metrics.get("equity_final", initial_capital))
    roi = float(metrics.get("net_profit_pct", 0.0))
    dd = float(metrics.get("max_drawdown_pct", 0.0))
    profit_factor = float(metrics.get("profit_factor", 0.0))
    sharpe = float(metrics.get("sharpe_ratio", 0.0))
    recovery = (roi / dd) if dd > 0 else 0.0
    net_profit = final_equity - initial_capital
    lines: list[str] = []
    lines.append("# Báo Cáo Kết Quả Pine Optimize (Tiếng Việt)")
    lines.append("")
    lines.append(f"Ngày tạo: {context.get('generated_at', '')}")
    lines.append("")
    lines.append("## 1) Vốn đầu vào")
    lines.append("")
    lines.append(f"- Vốn khởi điểm: **{initial_capital:,.2f} USD**")
    lines.append("")
    lines.append("## 2) Preset tốt nhất (Rank 1)")
    lines.append("")
    lines.append(f"- Pair: `{best.get('pair', '')}`")
    lines.append(f"- Timeframe: `{best.get('timeframe', '')}`")
    lines.append(f"- Session window: `{best.get('session_window', '')}`")
    lines.append(f"- Map: `{best.get('map_id', '')}`")
    lines.append(f"- Entry mode: `{params.get('entryMode', '')}`")
    lines.append(f"- SL/TP: `{metrics.get('sl_pct', 0)} / {metrics.get('tp_pct', 0)}`")
    lines.append("")
    lines.append("## 3) Chỉ số hiệu suất")
    lines.append("")
    lines.append(f"- **ROI**: `{roi:.2f}%`")
    lines.append(f"- **Net Profit**: `{net_profit:,.2f} USD`")
    lines.append(f"- **Max Drawdown (DD)**: `{dd:.2f}%`")
    lines.append(f"- **Profit Factor**: `{profit_factor:.2f}`")
    lines.append(f"- **Sharpe Ratio**: `{sharpe:.2f}`")
    lines.append(f"- **Recovery Factor**: `{recovery:.2f}`")
    lines.append(f"- Win Rate: `{float(metrics.get('win_rate_pct', 0.0)):.2f}%`")
    lines.append(f"- Trade Count: `{int(metrics.get('trade_count', 0))}`")
    lines.append("")
    lines.append("## 4) Khi nào lời nhất (tóm tắt)")
    lines.append("")
    session_top = (analysis.get("best_by_session_hour") or [{}])[0]
    month_top = (analysis.get("best_by_month_quarter") or [{}])[0]
    map_hour_top = (analysis.get("best_by_map_hour") or [{}])[0]
    if session_top:
        lines.append(
            f"- Theo giờ/phiên: `hour_utc={session_top.get('hour_utc')}` ({session_top.get('session')}) "
            f"với `net_profit_pct={session_top.get('net_profit_pct')}`"
        )
    if month_top:
        lines.append(
            f"- Theo tháng/quý: `{month_top.get('month')}` / `{month_top.get('quarter')}` "
            f"với `net_profit_pct={month_top.get('net_profit_pct')}`"
        )
    if map_hour_top:
        lines.append(
            f"- Theo map+giờ: `{map_hour_top.get('map_id')}` tại `hour_utc={map_hour_top.get('hour_utc')}` "
            f"với `net_profit_pct={map_hour_top.get('net_profit_pct')}`"
        )
    lines.append("")
    lines.append("## 5) File tham chiếu")
    lines.append("")
    lines.append(f"- Preset: `{context.get('preset_file', '')}`")
    lines.append("- JSON report: `best_when_report.json`")
    lines.append("- Markdown report: `best_when_report.md`")
    lines.append("- Markdown tiếng Việt: `README_best_result_vi.md`")
    lines.append("")
    return "\n".join(lines)
