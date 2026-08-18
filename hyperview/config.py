from __future__ import annotations

import json
import logging
import os
from copy import deepcopy
from pathlib import Path
from typing import Any

from .validators import (
    ALLOWED_DATAFORMATS,
    ALLOWED_MODES,
    ALLOWED_OBJECTIVES,
    ALLOWED_SESSIONS,
    require_choice,
    require_non_empty_string,
    require_number,
    require_pair_string,
    require_positive_int,
    require_positive_number,
)

_log = logging.getLogger(__name__)


_DEFAULTS: dict[str, Any] = {
    "bot_name": "hyperview",
    "timeframe": "1h",
    "session": "regular",
    "mode": "long",
    "initial_capital": 100_000,
    "data_dir": "data",
    "output_dir": "results",
    "strategy_path": "strategy",
    "dataformat": "csv",
    "strategy": "smc_swing",
    "pairlist": [],
    "add_config_files": [],
    "optimization": {
        "n_trials": 200,
        "objective": "net_profit_pct",
        "top_n": 10,
        "sl_range": {"min": 1.0, "max": 15.0},
        "tp_range": {"min": 1.0, "max": 15.0},
    },
    "smc": {
        "maps": [
            {"id": "h1_m5", "htf": "1h", "ltf": "5m"},
            {"id": "h4_m15", "htf": "4h", "ltf": "15m"},
        ],
        "entry_modes": ["both", "retest_ob", "aggressive"],
        "session_filter_optimize": True,
        "session_filter_default": True,
        "session_windows_utc": [[7, 17], [12, 22]],
        "time_budget_minutes": 10,
        "watchdog_seconds": 60,
        "coarse_trials": 30,
        "fine_trials": 120,
        "coarse_top_k": 6,
        "preset_top_n": 20,
        "min_signals": 8,
        "fine_span_ratio": 0.35,
    },
}

_SEARCH_PATHS = [
    Path("config.json"),
    Path("hyperview.json"),
]

_ENV_PREFIX = "HYPERVIEW__"

# Keys that are config metadata, not runtime settings.
_META_KEYS = {"$schema", "add_config_files"}


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load configuration from JSON file(s), env-var overrides, then validate.

    Resolution order (last wins):
      1. Built-in defaults
      2. Primary config file
      3. Additional config files (``add_config_files``)
      4. Environment variables (``HYPERVIEW__`` prefix)

    CLI arguments are applied *outside* this function by the caller.
    """
    config = deepcopy(_DEFAULTS)
    file_path = _resolve_config_path(path)

    # -- primary config file --
    if file_path is not None:
        user_config = _read_json(file_path)
        _deep_merge(config, user_config)

        # -- additional config files (paths relative to primary config dir) --
        extra_files = config.get("add_config_files", [])
        if isinstance(extra_files, list):
            base_dir = file_path.resolve().parent
            for extra in extra_files:
                extra_path = base_dir / extra
                if not extra_path.is_file():
                    raise FileNotFoundError(
                        f"Additional config file not found: {extra_path} "
                        f"(referenced in 'add_config_files')"
                    )
                _deep_merge(config, _read_json(extra_path))

    # -- environment variable overrides --
    _apply_env_overrides(config)

    # -- strip metadata keys before normalisation / validation --
    for key in _META_KEYS:
        config.pop(key, None)

    normalized = _normalize_config(config)
    _validate_config(normalized)
    return normalized


def resolve_config_path(path: str | Path | None = None) -> Path | None:
    """Return the primary config path used for loading, if any."""
    return _resolve_config_path(path)


def _resolve_config_path(path: str | Path | None) -> Path | None:
    if path is not None:
        candidate = Path(path)
        if candidate.is_file():
            return candidate
        raise FileNotFoundError(f"Config file not found: {candidate}")
    for candidate in _SEARCH_PATHS:
        if candidate.is_file():
            return candidate
    return None


def _read_json(file_path: Path) -> dict[str, Any]:
    """Read a JSON file and return the top-level object."""
    with open(file_path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a JSON object: {file_path}")
    return data


# ---------------------------------------------------------------------------
# Environment variable overrides  (HYPERVIEW__KEY / HYPERVIEW__SECTION__KEY)
# ---------------------------------------------------------------------------

def _apply_env_overrides(config: dict[str, Any]) -> None:
    """Merge ``HYPERVIEW__``-prefixed environment variables into *config*.

    ``__`` is the level separator, matching Freqtrade convention.
    Values are coerced: JSON-parseable strings are decoded first,
    otherwise plain strings are kept as-is.
    """
    overrides: list[str] = []
    for env_key, raw_value in os.environ.items():
        if not env_key.startswith(_ENV_PREFIX):
            continue
        parts = env_key[len(_ENV_PREFIX):].lower().split("__")
        if not all(parts):
            continue
        coerced = _coerce_env_value(raw_value)
        _set_nested(config, parts, coerced)
        overrides.append(env_key)

    if overrides:
        _log.info(
            "Config overrides from environment: %s",
            ", ".join(sorted(overrides)),
        )


def _coerce_env_value(raw: str) -> Any:
    """Attempt JSON decode; fall back to plain string."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return raw


def _set_nested(target: dict[str, Any], keys: list[str], value: Any) -> None:
    """Set a value in a nested dict, creating intermediate dicts as needed."""
    for key in keys[:-1]:
        if key not in target or not isinstance(target[key], dict):
            target[key] = {}
        target = target[key]
    target[keys[-1]] = value


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> None:
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


def _normalize_config(config: dict[str, Any]) -> dict[str, Any]:
    normalized = deepcopy(config)
    optimization = normalized.get("optimization", {})
    if isinstance(optimization, dict):
        normalized["optimization"] = dict(optimization)
        for key in ("sl_range", "tp_range"):
            range_config = normalized["optimization"].get(key, {})
            if isinstance(range_config, dict):
                normalized["optimization"][key] = dict(range_config)
    return normalized


def _validate_config(config: dict[str, Any]) -> None:
    require_non_empty_string(config, "bot_name")
    require_non_empty_string(config, "timeframe")
    require_choice(config, "session", ALLOWED_SESSIONS)
    require_choice(config, "mode", ALLOWED_MODES)
    require_positive_number(config, "initial_capital")
    require_non_empty_string(config, "data_dir")
    require_non_empty_string(config, "output_dir")
    require_non_empty_string(config, "strategy_path")
    require_choice(config, "dataformat", ALLOWED_DATAFORMATS)

    if "strategy" in config and config["strategy"] is not None:
        require_non_empty_string(config, "strategy")

    _validate_pairlist(config)

    optimization = config.get("optimization")
    if not isinstance(optimization, dict):
        raise ValueError("Config value 'optimization' must be an object")

    require_positive_int(optimization, "n_trials", prefix="optimization.")
    require_choice(optimization, "objective", ALLOWED_OBJECTIVES, prefix="optimization.")
    require_positive_int(optimization, "top_n", prefix="optimization.")

    _validate_range_config(optimization, "sl_range")
    _validate_range_config(optimization, "tp_range")
    _validate_smc_config(config)


def _validate_range_config(optimization: dict[str, Any], key: str) -> None:
    range_config = optimization.get(key)
    prefix = f"optimization.{key}."
    if not isinstance(range_config, dict):
        raise ValueError(f"Config value 'optimization.{key}' must be an object")

    require_number(range_config, "min", prefix=prefix)
    require_number(range_config, "max", prefix=prefix)

    min_value = float(range_config["min"])
    max_value = float(range_config["max"])
    if min_value > max_value:
        raise ValueError(
            f"Config value 'optimization.{key}.min' must be less than or equal to "
            f"'optimization.{key}.max'"
        )


def _validate_pairlist(config: dict[str, Any]) -> None:
    pairlist = config.get("pairlist", [])
    if not isinstance(pairlist, list):
        raise ValueError("Config value 'pairlist' must be a list of strings (e.g. 'EXCHANGE:SYMBOL')")
    for i, entry in enumerate(pairlist):
        require_pair_string(entry, key=f"pairlist[{i}]")


def _validate_smc_config(config: dict[str, Any]) -> None:
    smc = config.get("smc")
    if smc is None:
        return
    if not isinstance(smc, dict):
        raise ValueError("Config value 'smc' must be an object")

    maps = smc.get("maps", [])
    if not isinstance(maps, list) or not maps:
        raise ValueError("Config value 'smc.maps' must be a non-empty list")
    for idx, item in enumerate(maps):
        if not isinstance(item, dict):
            raise ValueError(f"Config value 'smc.maps[{idx}]' must be an object")
        require_non_empty_string(item, "id", prefix=f"smc.maps[{idx}].")
        require_non_empty_string(item, "htf", prefix=f"smc.maps[{idx}].")
        require_non_empty_string(item, "ltf", prefix=f"smc.maps[{idx}].")

    entry_modes = smc.get("entry_modes", [])
    if not isinstance(entry_modes, list) or not entry_modes:
        raise ValueError("Config value 'smc.entry_modes' must be a non-empty list")
    allowed_entry_modes = {"retest_ob", "aggressive", "both"}
    for idx, mode in enumerate(entry_modes):
        if mode not in allowed_entry_modes:
            raise ValueError(
                f"Config value 'smc.entry_modes[{idx}]' must be one of: {', '.join(sorted(allowed_entry_modes))}"
            )

    windows = smc.get("session_windows_utc", [])
    if not isinstance(windows, list) or not windows:
        raise ValueError("Config value 'smc.session_windows_utc' must be a non-empty list")
    for idx, item in enumerate(windows):
        if not isinstance(item, list) or len(item) != 2:
            raise ValueError(f"Config value 'smc.session_windows_utc[{idx}]' must be [start_hour, end_hour]")
        if any((isinstance(v, bool) or not isinstance(v, int) or v < 0 or v > 23) for v in item):
            raise ValueError(f"Config value 'smc.session_windows_utc[{idx}]' hours must be ints between 0 and 23")

    for key in ("time_budget_minutes", "watchdog_seconds", "coarse_trials", "fine_trials", "coarse_top_k", "preset_top_n", "min_signals"):
        value = smc.get(key)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"Config value 'smc.{key}' must be a positive integer")

    ratio = smc.get("fine_span_ratio")
    if isinstance(ratio, bool) or not isinstance(ratio, (int, float)) or not (0 < float(ratio) <= 1):
        raise ValueError("Config value 'smc.fine_span_ratio' must be > 0 and <= 1")
