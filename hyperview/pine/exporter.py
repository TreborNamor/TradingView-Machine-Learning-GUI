from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any

from .optimizer import PineCandidate

_INPUT_LINE_PATTERN = re.compile(
    r"^(?P<indent>\s*)(?P<name>[A-Za-z_]\w*)\s*=\s*input\.(?P<kind>\w+)\((?P<args>.*)\)\s*(?P<comment>//.*)?$"
)
_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_METRIC_TEMPLATE = "{symbol}_{tf}_{strategy}_np{net}_dd{dd}_pf{pf}_tc{trades}.pine"


def default_filename_template() -> str:
    return _METRIC_TEMPLATE


def build_metric_filename(
    *,
    template: str,
    pair: str,
    timeframe: str,
    strategy_name: str,
    candidate: PineCandidate,
) -> str:
    symbol = pair.split(":", 1)[-1]
    safe_symbol = sanitize_token(symbol)
    safe_strategy = sanitize_token(strategy_name)
    tf = compact_timeframe_slug(timeframe)
    return template.format(
        symbol=safe_symbol,
        tf=tf,
        strategy=safe_strategy,
        net=f"{candidate.metrics.net_profit_pct:.2f}",
        dd=f"{candidate.metrics.max_drawdown_pct:.2f}",
        pf=f"{candidate.metrics.profit_factor:.2f}",
        trades=f"{int(candidate.metrics.trade_count)}",
    )


def inject_default_inputs(pine_text: str, params: dict[str, Any]) -> tuple[str, int]:
    touched = 0
    rendered: list[str] = []
    for line in pine_text.splitlines():
        match = _INPUT_LINE_PATTERN.match(line)
        if match is None:
            rendered.append(line)
            continue
        name = match.group("name")
        if name not in params:
            rendered.append(line)
            continue
        raw_args = match.group("args") or ""
        parts = _split_top_level(raw_args)
        if len(parts) < 2:
            rendered.append(line)
            continue
        parts[0] = _to_pine_literal(params[name])
        comment = f" {match.group('comment')}" if match.group("comment") else ""
        rebuilt = (
            f"{match.group('indent')}{name} = input.{match.group('kind')}"
            f"({', '.join(parts)}){comment}"
        )
        rendered.append(rebuilt)
        touched += 1
    return "\n".join(rendered) + ("\n" if pine_text.endswith("\n") else ""), touched


def render_optimized_pine(
    *,
    source_text: str,
    candidate: PineCandidate,
    source_file: str,
    start: str | None,
    end: str | None,
    run_id: str,
) -> str:
    updated_source, touched = inject_default_inputs(source_text, candidate.params)
    header = [
        "// --- HyperView optimized snapshot ---",
        f"// run_id={run_id}",
        f"// source_file={source_file}",
        f"// pair={candidate.pair}",
        f"// timeframe={candidate.timeframe}",
        f"// period={start or 'auto'}->{end or 'auto'}",
        f"// net_profit_pct={candidate.metrics.net_profit_pct:.2f}",
        f"// max_drawdown_pct={candidate.metrics.max_drawdown_pct:.2f}",
        f"// profit_factor={candidate.metrics.profit_factor:.2f}",
        f"// trade_count={int(candidate.metrics.trade_count)}",
        f"// inputs_injected={touched}",
        "",
    ]
    return "\n".join(header) + updated_source


def resolve_optimization_report_dir(
    *,
    output_dir: str,
    pair: str,
    timeframe: str,
    explicit_report_dir: str | None,
) -> Path:
    if explicit_report_dir:
        return Path(explicit_report_dir)
    symbol = pair.split(":", 1)[-1]
    return Path(output_dir) / "optimizations" / sanitize_token(symbol) / timeframe.lower()


def sanitize_token(value: str) -> str:
    lowered = value.strip().lower()
    sanitized = _NON_ALNUM.sub("_", lowered).strip("_")
    return sanitized or "na"


def compact_timeframe_slug(value: str) -> str:
    text = value.strip().lower()
    matched = re.match(r"^(\d+)([mhdw])$", text)
    if matched:
        return f"{matched.group(2)}{matched.group(1)}"
    return sanitize_token(text)


def utc_run_id() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).strftime("%Y%m%dT%H%M%SZ")


def _split_top_level(text: str) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    depth = 0
    quote: str | None = None
    escaped = False
    for ch in text:
        if quote is not None:
            current.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            continue
        if ch in {"'", '"'}:
            quote = ch
            current.append(ch)
            continue
        if ch in {"(", "[", "{"}:
            depth += 1
            current.append(ch)
            continue
        if ch in {")", "]", "}"}:
            depth = max(0, depth - 1)
            current.append(ch)
            continue
        if ch == "," and depth == 0:
            chunks.append("".join(current).strip())
            current = []
            continue
        current.append(ch)
    if current:
        chunks.append("".join(current).strip())
    return chunks


def _to_pine_literal(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.6f}".rstrip("0").rstrip(".")
    escaped = str(value).replace('"', '\\"')
    return f'"{escaped}"'
