from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .validators import (
    ALLOWED_ADJUSTMENTS,
    ALLOWED_MODES,
    ALLOWED_OBJECTIVES,
    ALLOWED_SESSIONS,
    check_choice,
    check_non_empty_string,
    check_positive_number,
    require_pair_string,
)
_PRESET_SCOPE_KEYS = ("pair", "timeframe", "session", "adjustment", "mode")

# Built once at import time — avoids recreating these sets on every _validate_payload call.
_ALLOWED_TOP_LEVEL_KEYS: frozenset[str] = frozenset({"strategy", "updated_at", "presets"})
_ALLOWED_PRESET_KEYS: frozenset[str] = frozenset({
    "pair", "timeframe", "session", "adjustment", "mode",
    "sl", "tp", "objective", "search_method", "updated_at", "metrics",
    "rank", "map_id", "session_window", "analysis_tags", "min_trades_gate", "meta",
})


def strategy_preset_path(output_dir: str | Path, strategy: str) -> Path:
    return Path(output_dir) / f"{strategy}_presets.json"


def load_strategy_presets(path: str | Path) -> dict[str, Any]:
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Preset file not found: {file_path}")
    with open(file_path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Preset file must contain a JSON object: {file_path}")
    normalized = _normalize_payload(data)
    _validate_payload(normalized)
    return normalized


def find_preset(
    path: str | Path,
    *,
    strategy: str,
    pair: str,
    timeframe: str,
    session: str,
    adjustment: str,
    mode: str,
    rank: int | None = None,
) -> dict[str, Any] | None:
    payload = load_strategy_presets(path)
    if payload.get("strategy") != strategy:
        raise ValueError(
            f"Preset file strategy mismatch: expected '{strategy}', found '{payload.get('strategy')}'."
        )
    scope = {
        "pair": pair,
        "timeframe": timeframe,
        "session": session,
        "adjustment": adjustment,
        "mode": mode,
    }
    matches = [preset for preset in payload["presets"] if all(preset.get(key) == value for key, value in scope.items())]
    if not matches:
        return None
    if rank is not None:
        for preset in matches:
            if int(preset.get("rank", 1)) == rank:
                return dict(preset)
    matches = sorted(matches, key=lambda item: int(item.get("rank", 1)))
    return dict(matches[0])
    

def save_top_presets(
    path: str | Path,
    *,
    strategy: str,
    pair: str,
    timeframe: str,
    session: str,
    adjustment: str,
    mode: str,
    objective: str,
    search_method: str,
    items: list[dict[str, Any]],
) -> Path:
    file_path = Path(path)
    payload = _read_existing_payload(file_path, strategy)

    scope = {
        "pair": pair,
        "timeframe": timeframe,
        "session": session,
        "adjustment": adjustment,
        "mode": mode,
    }
    payload["presets"] = [entry for entry in payload["presets"] if not _matches_scope(entry, scope)]
    now = _utc_now()
    cleaned: list[dict[str, Any]] = []
    for index, item in enumerate(items, start=1):
        preset: dict[str, Any] = {
            **scope,
            "sl": float(item["sl"]),
            "tp": float(item["tp"]),
            "objective": objective,
            "search_method": search_method,
            "updated_at": now,
            "rank": int(item.get("rank", index)),
        }
        if item.get("map_id") is not None:
            preset["map_id"] = str(item["map_id"])
        if item.get("session_window") is not None:
            preset["session_window"] = str(item["session_window"])
        if item.get("analysis_tags") is not None:
            preset["analysis_tags"] = item["analysis_tags"]
        if item.get("min_trades_gate") is not None:
            preset["min_trades_gate"] = int(item["min_trades_gate"])
        if item.get("metrics") is not None:
            preset["metrics"] = item["metrics"]
        if item.get("meta") is not None:
            preset["meta"] = item["meta"]
        cleaned.append(preset)

    payload["updated_at"] = now
    payload["presets"].extend(cleaned)
    payload["presets"] = sorted(
        payload["presets"],
        key=lambda item: (
            item["pair"],
            item["timeframe"],
            item["session"],
            item["adjustment"],
            item["mode"],
            int(item.get("rank", 1)),
        ),
    )

    _validate_payload(payload)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(payload, indent=4) + "\n", encoding="utf-8")
    return file_path


def save_best_preset(
    path: str | Path,
    *,
    strategy: str,
    pair: str,
    timeframe: str,
    session: str,
    adjustment: str,
    mode: str,
    sl: float,
    tp: float,
    objective: str,
    search_method: str,
    metrics: dict[str, Any] | None = None,
) -> Path:
    file_path = Path(path)
    payload = _read_existing_payload(file_path, strategy)
    preset: dict[str, Any] = {
        "pair": pair,
        "timeframe": timeframe,
        "session": session,
        "adjustment": adjustment,
        "mode": mode,
        "sl": float(sl),
        "tp": float(tp),
        "objective": objective,
        "search_method": search_method,
        "updated_at": _utc_now(),
    }
    if metrics is not None:
        preset["metrics"] = metrics

    payload["updated_at"] = _utc_now()
    payload["presets"] = [
        item for item in payload["presets"] if not _matches_scope(item, preset)
    ]
    payload["presets"].append(preset)
    payload["presets"] = sorted(
        payload["presets"],
        key=lambda item: (
            item["pair"],
            item["timeframe"],
            item["session"],
            item["adjustment"],
            item["mode"],
        ),
    )

    _validate_payload(payload)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(payload, indent=4) + "\n", encoding="utf-8")
    return file_path


def _read_existing_payload(file_path: Path, strategy: str) -> dict[str, Any]:
    if not file_path.exists():
        return {
            "strategy": strategy,
            "updated_at": _utc_now(),
            "presets": [],
        }

    payload = load_strategy_presets(file_path)
    if payload.get("strategy") != strategy:
        raise ValueError(
            f"Preset file strategy mismatch: expected '{strategy}', found '{payload.get('strategy')}'."
        )
    return deepcopy(payload)


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    # deepcopy already produces independent copies of all nested dicts — no further wrapping needed.
    return deepcopy(payload)


def _validate_payload(payload: dict[str, Any]) -> None:
    unknown_top_level = sorted(set(payload) - _ALLOWED_TOP_LEVEL_KEYS)
    if unknown_top_level:
        raise ValueError(
            f"Preset file contains unsupported top-level keys: {', '.join(unknown_top_level)}"
        )

    check_non_empty_string(payload.get("strategy"), "strategy")
    check_non_empty_string(payload.get("updated_at"), "updated_at")
    presets = payload.get("presets")
    if not isinstance(presets, list):
        raise ValueError("Preset file value 'presets' must be a list")

    for index, preset in enumerate(presets):
        prefix = f"presets[{index}]"
        if not isinstance(preset, dict):
            raise ValueError(f"Preset file value '{prefix}' must be an object")
        unknown_keys = sorted(set(preset) - _ALLOWED_PRESET_KEYS)
        if unknown_keys:
            raise ValueError(
                f"Preset file value '{prefix}' contains unsupported keys: {', '.join(unknown_keys)}"
            )

        require_pair_string(preset.get("pair"), key=f"{prefix}.pair", label="Preset file value")
        check_non_empty_string(preset.get("timeframe"), f"{prefix}.timeframe")
        check_choice(preset.get("session"), ALLOWED_SESSIONS, f"{prefix}.session")
        check_choice(preset.get("adjustment"), ALLOWED_ADJUSTMENTS, f"{prefix}.adjustment")
        check_choice(preset.get("mode"), ALLOWED_MODES, f"{prefix}.mode")
        check_positive_number(preset.get("sl"), f"{prefix}.sl")
        check_positive_number(preset.get("tp"), f"{prefix}.tp")
        check_choice(preset.get("objective"), ALLOWED_OBJECTIVES, f"{prefix}.objective")
        check_choice(preset.get("search_method"), frozenset({"bayesian", "coarse_to_fine"}), f"{prefix}.search_method")
        check_non_empty_string(preset.get("updated_at"), f"{prefix}.updated_at")
        if "rank" in preset and (isinstance(preset.get("rank"), bool) or int(preset["rank"]) <= 0):
            raise ValueError(f"Preset file value '{prefix}.rank' must be a positive integer")
        if "map_id" in preset:
            check_non_empty_string(preset.get("map_id"), f"{prefix}.map_id")
        if "session_window" in preset:
            check_non_empty_string(preset.get("session_window"), f"{prefix}.session_window")
        if "analysis_tags" in preset and not isinstance(preset.get("analysis_tags"), list):
            raise ValueError(f"Preset file value '{prefix}.analysis_tags' must be a list")
        if "min_trades_gate" in preset and (isinstance(preset.get("min_trades_gate"), bool) or int(preset["min_trades_gate"]) <= 0):
            raise ValueError(f"Preset file value '{prefix}.min_trades_gate' must be a positive integer")
        if "metrics" in preset:
            _validate_metrics(preset["metrics"], f"{prefix}.metrics")
        if "meta" in preset and not isinstance(preset.get("meta"), dict):
            raise ValueError(f"Preset file value '{prefix}.meta' must be an object")


def _matches_scope(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return all(left.get(key) == right.get(key) for key in _PRESET_SCOPE_KEYS)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _validate_metrics(value: Any, key: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"Preset file value '{key}' must be an object")
