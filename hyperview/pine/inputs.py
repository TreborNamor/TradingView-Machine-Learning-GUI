from __future__ import annotations

from dataclasses import dataclass
import ast
import re
from typing import Any, Literal

InputType = Literal["int", "float", "string", "bool", "timeframe", "session"]
DimensionType = Literal["int", "float", "categorical"]

_INPUT_PATTERN = re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*input\.(\w+)\((.*)\)\s*$")
_SMC_KEY_MAP: dict[str, str] = {
    "htfTf": "htf_timeframe",
    "entryMode": "entry_mode",
    "sweepLookback": "htf_swing_lookback",
    "chochLookback": "choch_lookback",
    "confirmBars": "confirm_window_bars",
    "obLookback": "ob_lookback_bars",
    "retestWindow": "retest_window_bars",
    "atrLength": "atr_length",
    "slBufferAtr": "sl_buffer_atr",
    "rrTarget": "rr_target",
    "sessionFilter": "session_filter_enabled",
    "sessionA": "sessionA",
    "sessionB": "sessionB",
}

@dataclass(frozen=True)
class PineInputSpec:
    name: str
    input_type: InputType
    default: Any
    label: str
    minval: float | int | None = None
    maxval: float | int | None = None
    step: float | int | None = None
    options: list[Any] | None = None
    strategy_key: str | None = None
    impacts_pnl: bool = True

@dataclass(frozen=True)
class SearchDimension:
    name: str
    dim_type: DimensionType
    strategy_key: str
    impacts_pnl: bool
    default: Any
    values: list[Any] | None = None
    minval: float | int | None = None
    maxval: float | int | None = None
    step: float | int | None = None

def extract_pine_inputs(pine_text: str) -> list[PineInputSpec]:
    specs: list[PineInputSpec] = []
    for raw in pine_text.splitlines():
        match = _INPUT_PATTERN.match(raw.strip())
        if match is None:
            continue
        name, kind, raw_args = match.group(1), match.group(2), match.group(3)
        parsed = _parse_input_args(raw_args)
        if parsed is None:
            continue
        default, label, kwargs = parsed
        input_type = _normalize_input_type(kind)
        if input_type is None:
            continue
        strategy_key = _SMC_KEY_MAP.get(name)
        impacts_pnl = strategy_key is not None and _token_usage_count(pine_text, name) > 1
        specs.append(
            PineInputSpec(
                name=name,
                input_type=input_type,
                default=_coerce_literal(default),
                label=str(_coerce_literal(label)),
                minval=_to_number(kwargs.get("minval")),
                maxval=_to_number(kwargs.get("maxval")),
                step=_to_number(kwargs.get("step")),
                options=_parse_options(kwargs.get("options")),
                strategy_key=strategy_key,
                impacts_pnl=impacts_pnl,
            )
        )
    return specs

def resolve_search_dimensions(inputs: list[PineInputSpec]) -> tuple[list[SearchDimension], list[str]]:
    dimensions: list[SearchDimension] = []
    warnings: list[str] = []
    for spec in inputs:
        if spec.strategy_key is None:
            warnings.append(f"Input '{spec.name}' has no mapped strategy key; skipping.")
            continue
        if not spec.impacts_pnl:
            warnings.append(f"Input '{spec.name}' appears display-only; excluded from objective.")
            continue
        dim = _spec_to_dimension(spec)
        if dim is None:
            warnings.append(f"Input '{spec.name}' has unsupported shape; skipping.")
            continue
        dimensions.append(dim)
    return dimensions, warnings

def _spec_to_dimension(spec: PineInputSpec) -> SearchDimension | None:
    if spec.input_type in {"string", "bool", "timeframe", "session"}:
        values = _categorical_values(spec)
        if not values:
            return None
        return SearchDimension(
            name=spec.name,
            dim_type="categorical",
            strategy_key=spec.strategy_key or spec.name,
            impacts_pnl=spec.impacts_pnl,
            default=spec.default,
            values=values,
        )
    if spec.input_type == "int":
        minval = int(spec.minval if spec.minval is not None else max(1, int(spec.default) // 2))
        maxval = int(spec.maxval if spec.maxval is not None else max(minval + 1, int(spec.default) * 2))
        step = int(spec.step if spec.step is not None else 1)
        return SearchDimension(
            name=spec.name,
            dim_type="int",
            strategy_key=spec.strategy_key or spec.name,
            impacts_pnl=spec.impacts_pnl,
            default=int(spec.default),
            minval=minval,
            maxval=maxval,
            step=max(1, step),
        )
    if spec.input_type == "float":
        minval = float(spec.minval if spec.minval is not None else max(0.0, float(spec.default) * 0.5))
        maxval = float(spec.maxval if spec.maxval is not None else max(minval + 0.01, float(spec.default) * 2.0))
        step = float(spec.step if spec.step is not None else 0.05)
        return SearchDimension(
            name=spec.name,
            dim_type="float",
            strategy_key=spec.strategy_key or spec.name,
            impacts_pnl=spec.impacts_pnl,
            default=float(spec.default),
            minval=minval,
            maxval=maxval,
            step=max(0.0001, step),
        )
    return None

def _categorical_values(spec: PineInputSpec) -> list[Any]:
    if spec.input_type == "session":
        base = str(spec.default)
        windows = {base}
        for shifted in (-2, -1, 1, 2):
            windows.add(_shift_session(base, shifted))
        return sorted(windows)
    if spec.input_type == "timeframe":
        base = str(spec.default)
        candidates = {"15", "30", "60", "120", "240", "1D", base}
        return sorted(candidates)
    if spec.options:
        return list(spec.options)
    if spec.input_type == "bool":
        return [True, False]
    return [spec.default]

def _shift_session(value: str, shift_hours: int) -> str:
    if not re.match(r"^\d{4}-\d{4}$", value):
        return value
    start_raw, end_raw = value.split("-", 1)
    start_hour = (int(start_raw[:2]) + shift_hours) % 24
    end_hour = (int(end_raw[:2]) + shift_hours) % 24
    return f"{start_hour:02d}{start_raw[2:]}-{end_hour:02d}{end_raw[2:]}"

def _normalize_input_type(value: str) -> InputType | None:
    lowered = value.lower()
    if lowered in {"int", "float", "string", "bool", "timeframe", "session"}:
        return lowered  # type: ignore[return-value]
    return None

def _parse_input_args(raw_args: str) -> tuple[str, str, dict[str, str]] | None:
    parts = _split_top_level(raw_args)
    if len(parts) < 2:
        return None
    default = parts[0].strip()
    label = parts[1].strip()
    kwargs: dict[str, str] = {}
    for part in parts[2:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        kwargs[key.strip()] = value.strip()
    return default, label, kwargs

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

def _coerce_literal(raw: str) -> Any:
    text = raw.strip()
    lowered = text.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return text.strip('"').strip("'")

def _parse_options(raw: str | None) -> list[Any] | None:
    if raw is None:
        return None
    try:
        value = ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return None
    if isinstance(value, list):
        return value
    return None

def _to_number(raw: str | None) -> float | int | None:
    if raw is None:
        return None
    value = _coerce_literal(raw)
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return value
    return None

def _token_usage_count(source: str, token: str) -> int:
    return len(re.findall(rf"\b{re.escape(token)}\b", source))
