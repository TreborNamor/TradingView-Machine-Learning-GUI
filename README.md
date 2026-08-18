# HyperView

**Turn TradingView ideas into testable, terminal-speed trading systems.**

HyperView is a CLI-first toolkit for downloading TradingView market data, backtesting Python strategies with Pine-like execution behavior, and optimizing parameters in a repeatable workflow.

Vietnamese version: [README.vi.md](README.vi.md)

## Support This Project

If you discover a strong strategy using this repo, please consider giving the project a **star** and **forking** it to support further development.

## Pain Points

- Manual optimization on TradingView charts is slow, hard to reproduce, and difficult to audit.
- Results often diverge between Pine and local scripts because fill assumptions differ.
- Data, presets, and reports are scattered across CSVs, notebooks, and ad-hoc scripts.
- Multi-strategy and multi-pair research takes too long without a standardized pipeline.

## Solution

- A unified CLI workflow: `download -> signal -> backtest -> optimize -> export artifacts`.
- A TradingView-like backtester (next-bar-open entries + intrabar SL/TP path simulation).
- Automatic preset/report/context storage for comparison and reproducible reruns.
- Pine input optimization with best-parameter injection into exported Pine scripts.

## Key Features

- Historical download from TradingView websocket (up to ~40K bars with eligible authenticated session).
- Python strategy framework + TA-Lib (20 wrapped indicators + direct TA-Lib access).
- Backtesting with mathematically correct portfolio aggregation from combined equity curves.
- SL/TP optimization via Optuna (TPE), with top preset persistence.
- Two-stage Pine optimization + batch optimization for multiple strategy files.
- Structured artifacts (`data/`, `results/`, `strategies/raw/`, `strategies/optimized/`).

## FAQ (Pro Account & Tick Data)

### Can I use HyperView without a TradingView Pro account?

Yes. You can still use download, backtest, and optimization features without Pro.  
In practice, data depth is typically lower for anonymous/non-authenticated sessions (often around ~5K bars), while authenticated paid sessions can reach higher limits (up to ~40K bars, depending on account/session availability).

### Does HyperView support tick data?

No. HyperView is candle/timeframe based (`1m`, `5m`, `15m`, `1h`, etc.), not tick-by-tick data stream based.

### Is `1m` data equivalent to tick data?

No. `1m` is still aggregated OHLCV bar data, not raw market ticks.

### Can this be used for tick-level/HFT validation?

Not natively in the current architecture. The backtester uses bar-level + intrabar-path assumptions, not full tick replay.

### Do I need any TradingView API key?

No. The downloader uses TradingView websocket/session mechanics and optional local browser session credentials.

## Practical Outcomes

- Faster strategy research loops by replacing chart-click workflows with automated CLI pipelines.
- Easier team collaboration through consistent presets, reports, and saved contexts.
- Lower mismatch risk when moving from Pine ideas to quantitative validation.
- Better scaling for multi-strategy, multi-symbol, and multi-timeframe experiments.

## Improvements Over The Original Fork Source

The fork improvements are not only cosmetic; they are implemented as concrete workflow tasks:

1. **CLI Standardization Task**
   - Unified command entry around `tradingview-backtest`.
   - Kept backward-compatible aliases: `hyperview`, `python -m hyperview`.
   - Goal: reduce team friction across local terminal + AI CLI usage.

2. **Pine Optimization Pipeline Task**
   - Added optimized Pine export with best params injected into defaults.
   - Added compact filename metrics (`np/dd/pf/tc`) for fast scanning.
   - Added per-run metadata headers in exported Pine snapshots.

3. **Batch Orchestration Task**
   - Added batch runner to optimize multiple Pine files from `strategies/raw/`.
   - Added matrix execution for symbols/timeframes.
   - Added leaderboard outputs for top results aggregation.

4. **Artifact Contract Task**
   - Standardized directories:
     - `strategies/raw/`
     - `strategies/optimized/`
     - `results/optimizations/<symbol>/<timeframe>/`
   - Goal: deterministic outputs for commit/push/audit and easier collaboration.

5. **Automation & Onboarding Task**
   - Added cross-platform bootstrap scripts (`.cmd`, `.ps1`, `.sh`).
   - Added GitHub release workflow and build smoke checks.
   - Added Codex/Claude quick workflow guidance in docs.

## Prerequisites

### Core runtime requirements

- **Python 3.11+**
- **TA-Lib** — installed automatically by `pip install`. Pre-built wheels are available for major OS/Python combinations.
- **rich** — installed automatically for CLI tables/panels/progress UI.
- **Firefox** *(optional)* — for authenticated TradingView session reuse (higher historical bar limits).

### Additional requirements to use fork improvements fully

- **Git + GitHub CLI (`gh`)** — needed for release automation, fork sync, and GitHub-native workflow management.
- **One of `uvx` / `pipx` / `pip`** — needed for portable install/run modes documented in this fork.
- **Writable workspace for artifacts** — required because this fork intentionally tracks richer outputs in:
  - `data/`
  - `results/`
  - `strategies/raw/`
  - `strategies/optimized/`

### Verification baseline (recommended before serious runs)

```bash
python -m unittest discover -s tests -v
python -m hyperview --help
python -m hyperview list-strategies
```

## Install & Run Anywhere

Canonical CLI command is now `tradingview-backtest`.  
Backwards-compatible aliases still work: `tvbacktest`, `hyperview`, and `python -m hyperview`.

### Option A (Recommended, npx-like): `uvx`

```bash
# Run directly from GitHub (no long-lived install)
uvx --from git+https://github.com/<org>/tradingview-backtest.git tradingview-backtest --help
```

```bash
# After publishing to PyPI
uvx tradingview-backtest --help
```

### Option B (npm -g-like): `pipx`

```bash
pipx install tradingview-backtest
tradingview-backtest --help
```

### Option C (Universal fallback): `pip`

```bash
python -m pip install tradingview-backtest
python -m hyperview --help
```

### Bootstrap Scripts (from this repo)

```bash
# Windows (cmd)
scripts\bootstrap.cmd local

# Windows (PowerShell)
.\scripts\bootstrap.ps1 -Mode local

# Linux/macOS
./scripts/bootstrap.sh local
```

## Quick Start (Project Development)

```bash
# Install in editable mode (creates `tradingview-backtest`, `tvbacktest`, and `hyperview`)
pip install -e .

# Download data for specific pairs
tradingview-backtest download-data --pairs NASDAQ:NFLX NASDAQ:AAPL --timeframe 1h --session extended

# Or define your pairs in config.json and download multiple timeframes at once:
tradingview-backtest download-data --timeframe 1h 15m

# Run a single backtest (uses config pairlist)
tradingview-backtest backtest --sl 3.23 --tp 13.06 --mode long

# Or target a specific symbol using values from a hyperopt preset file
tradingview-backtest backtest --symbol NASDAQ:NFLX --preset-file results/adx_stochastic_presets.json

# Hyper-optimize SL/TP across all pairs in config
tradingview-backtest hyperopt --mode long

# List cached data and registered strategies
tradingview-backtest list-data
tradingview-backtest list-strategies
```

You can still run via `python -m hyperview` for environments that prefer module execution.

Python bytecode is redirected into the project-level `.pycache/` directory, so runtime imports do not create scattered `__pycache__` folders under `hyperview/` or `strategy/`.

## Fast Workflow With Codex CLI / Claude Code

This repo works well with both **Codex CLI** and **Claude Code** for AI-assisted development.

### 1) One-time setup

```bash
# Clone repo
git clone https://github.com/hungpixi/tradingview-backtest.git
cd tradingview-backtest

# Bootstrap local env (cross-platform script)
# Windows:
scripts\bootstrap.cmd local
# Linux/macOS:
./scripts/bootstrap.sh local
```

### 2) Prompt examples for AI CLI

- `"Run pine-batch-optimize for OANDA:XAUUSD on 15m and summarize best result."`
- `"Add a new CLI flag for pine-optimize and include unit tests."`
- `"Refactor hyperview/cli/pine.py but keep command behavior backward-compatible."`
- `"Review this branch for regressions in backtest and pine optimize flow."`

### 3) Quick verification before commit

```bash
python -m unittest discover -s tests -v
python -m hyperview --help
python -m hyperview list-strategies
```

### 4) Tips for better AI output quality

- Be explicit about the goal and desired output (specific files/reports/commands).
- Always require verification commands before an AI says work is done.
- For larger changes, ask for scoped commits (`feat`, `chore`, `docs`).
- In this repo, prioritize real CLI validation (`download-data`, `backtest`, `hyperopt`, `pine-optimize`) rather than code-only edits.

## How It Works

1. **Download** — Connects to TradingView's websocket using your existing Firefox session cookies. Supports up to 40K historical bars on paid plans with automatic backfill.
2. **Signal** — Runs a pluggable strategy (e.g. the included MACD+RSI or ADX+Stochastic) in pure Python with TA-Lib indicator parity.
3. **Backtest** — Simulates trades bar-by-bar using TradingView-parity fill assumptions (next-bar-open entry, intrabar SL/TP exit ordering). Multi-pair runs produce a true **PORTFOLIO** aggregate row with combined equity-curve statistics.
4. **Hyper-Optimize** — Runs Bayesian optimization (Optuna TPE) across SL/TP combinations, then updates a strategy preset file with the best result for each pair/context.

## Terminal Output

Both the backtest and hyperopt commands produce styled terminal output using [rich](https://github.com/Textualize/rich):

- **Backtest summary** — A bordered table with colored directional arrows (▲ green for gains, ▼ red for losses) on Return, Drawdown, Expectancy, and Worst Trade, using readable short labels that fit a normal terminal width. When multiple pairs are run, a **PORTFOLIO** row is appended with mathematically correct aggregate statistics computed from a combined equity curve (not simple averages).
- **Hyperopt results** — A panel header showing strategy/mode/timeframe, bullet-point data and signal summaries per pair, and a top-N results table with cyan-highlighted parameter columns (SL/TP) visually separated from metric columns.

## Repository Layout

```
pyproject.toml              Package metadata & CLI entry point
config.json                 Default configuration (timeframe, pairlist, opt ranges)
config.schema.json          JSON Schema for editor validation & autocompletion
data/                       Cached candle CSVs (auto-generated)
results/                    Optimization presets & reports (auto-generated)
strategies/raw/             Source Pine scripts for optimization input
strategies/optimized/       Best optimized Pine exports (filename includes metrics)
```

### `strategy/` — Pluggable Strategy Framework

```
strategy/
├── __init__.py             Plugin registry & auto-discovery
├── base.py                 BaseStrategy ABC & prepare_candles()
├── indicators.py           TA-Lib wrappers, conversion helpers & signal toolkit
├── adx_stochastic.py       ADX+Stochastic strategy
└── macd_rsi.py             MACD+RSI strategy
```

### `hyperview/` — Core Engine

```
hyperview/
├── __main__.py             Module entry point (python -m hyperview)
├── config.py               Config loader (JSON + CLI overrides + env vars)
├── models.py               Shared dataclasses (CandleRequest, Trade, BacktestMetrics, …)
├── presets.py              Preset load/save for optimized SL/TP parameters
├── validators.py           Configuration & preset validation rules
├── runtime.py              Bytecode cache redirection
│
├── cli/                    CLI router & subcommand handlers
│   ├── __init__.py         Argument parser & main() dispatcher
│   ├── formatting.py       Shared formatting helpers (rich tables, arrow decorators)
│   ├── backtest.py         backtest command
│   ├── download.py         download-data command
│   ├── hyperopt.py         hyperopt command
│   └── list.py             list-data & list-strategies commands
│
├── backtest/
│   └── engine.py           TradingView-parity OHLC simulator
│
├── downloader/
│   ├── client.py           TradingView websocket downloader & cache orchestration
│   ├── cache.py            CSV-backed local candle cache
│   ├── credentials.py      Firefox credential extraction
│   ├── session.py          WebSocket chart session manager
│   └── timeframes.py       Timeframe constants & utilities
│
└── hyperopt/
    └── optimizer.py        Bayesian optimizer (Optuna TPE)
```

## Configuration

HyperView loads defaults from `config.json` at the project root. CLI flags always override config values.

The sample below shows a customized setup; if a key is omitted, HyperView falls back to runtime defaults.

```json
{
    "timeframe": "1h",
    "session": "regular",
    "mode": "long",
    "strategy": "adx_stochastic",
    "initial_capital": 100000,
    "data_dir": "data",
    "output_dir": "results",
    "pairlist": [
        "NASDAQ:NFLX",
        "NASDAQ:TSLA",
        "COINBASE:BTCUSD",
        "COINBASE:ETHUSD"
    ],
    "optimization": {
        "n_trials": 200,
        "objective": "net_profit_pct",
        "top_n": 10,
        "sl_range": { "min": 1.0, "max": 15.0 },
        "tp_range": { "min": 1.0, "max": 15.0 }
    }
}
```

Use `--config /path/to/custom.json` to load a different file.

### Pairlist

The `pairlist` array defines the symbols you want to work with. Every entry must use the `EXCHANGE:SYMBOL` format — this lets you mix pairs from different exchanges in a single config:

```json
"pairlist": [
    "NASDAQ:NFLX",
    "NASDAQ:TSLA",
    "NASDAQ:AAPL",
    "COINBASE:BTCUSD"
]
```

When you run a command without `--pairs` or `--symbol`, HyperView automatically uses the config pairlist — downloading, backtesting, or optimizing every pair in sequence. If you pass `--pairs` or `--symbol` on the CLI, the config pairlist is ignored for that run.

You can maintain separate config files for different asset classes:

```bash
hyperview --config stocks.json download-data
hyperview --config crypto.json hyperopt --mode long
```

## CLI Reference

All command examples below can use `tradingview-backtest` (recommended) or legacy alias `hyperview`.

## Migration Notes

- `hyperview` command is still supported for backward compatibility.
- New canonical command for docs/releases is `tradingview-backtest`.
- Short alias `tvbacktest` is also available.

### `download-data` — Fetch Candle Data

```bash
# Download all pairs from config pairlist
hyperview download-data

# Or specify pairs directly, including multiple timeframes
hyperview download-data --pairs NASDAQ:NFLX NASDAQ:AAPL NASDAQ:TSLA --timeframe 1h 15m --start 2023-01-03
```

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--pairs` | No | config pairlist | One or more `EXCHANGE:SYMBOL` pairs (overrides pairlist) |
| `--timeframe` | No | config | One or more bar intervals: `1m` `5m` `15m` `1h` `4h` `1d` etc. |
| `--start` / `--end` | No | — | Date range (ISO format) |
| `--session` | No | config | `regular` or `extended` |
| `--adjustment` | No | `splits` | Price adjustment (`splits`, `dividends`, `none`) |

### `backtest` — Single Strategy Evaluation

```bash
# Backtest all pairs from config pairlist
hyperview backtest --sl 5.0 --tp 5.0 --mode long --start 2023-01-03

# Or target a specific symbol using a preset file created by hyperopt
hyperview backtest --symbol NASDAQ:NFLX --preset-file results/adx_stochastic_presets.json --start 2023-01-03
```

If `--sl` and `--tp` are omitted, HyperView looks for a matching entry in the provided `--preset-file` using `pair + timeframe + session + adjustment + mode`. CLI values still override preset-file values.

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--symbol` | No | config pairlist | `EXCHANGE:SYMBOL` pair (overrides pairlist) |
| `--sl` | No* | — | Stop-loss % (*required unless a matching `--preset-file` entry exists) |
| `--tp` | No* | — | Take-profit % (*required unless a matching `--preset-file` entry exists) |
| `--preset-file` | No | auto-detected | Path to a strategy preset JSON (auto-detects `<strategy>_presets.json` in output dir) |
| `--strategy` | No | config | Strategy name (e.g. `macd_rsi`, `adx_stochastic`) |
| `--mode` | No | `long` | `long`, `short`, or `both` |
| `--timeframe`, `--session`, `--adjustment`, `--start`, `--end` | No | config / defaults | Standard filters |

### `hyperopt` — Hyper-Optimize SL/TP

```bash
# Optimize all pairs from config pairlist (runs one optimization per pair)
hyperview hyperopt --n-trials 300

# Or target a specific symbol
hyperview hyperopt --symbol NASDAQ:NFLX --n-trials 300
```

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--symbol` | No | config pairlist | `EXCHANGE:SYMBOL` pair (overrides pairlist) |
| `--sl-min`, `--sl-max` | No | config | Stop-loss % search range |
| `--tp-min`, `--tp-max` | No | config | Take-profit % search range |
| `--n-trials` | No | config | Number of Bayesian optimization trials (default: 200) |
| `--objective` | No | config | `net_profit_pct` `profit_factor` `win_rate_pct` `max_drawdown_pct` `trade_count` |
| `--top-n` | No | config | Number of top candidates to keep |
| `--strategy`, `--mode`, `--timeframe`, `--adjustment`, etc. | No | config / defaults | Standard filters |

### `list-data` — Show Cached Datasets

```bash
hyperview list-data
```

### `list-strategies` — Show Available Strategies

```bash
hyperview list-strategies
```

### `pine-optimize` — Optimize Pine Inputs + Export Best Pine

```bash
hyperview pine-optimize --pine-file strategies/raw/smc_swing_strategy.pine --symbol OANDA:XAUUSD --timeframe 15m
```

- Exports best Pine by default to `strategies/optimized/`.
- Default optimized filename template:
  `{symbol}_{tf}_{strategy}_np{net}_dd{dd}_pf{pf}_tc{trades}.pine`
- Pair/timeframe reports are written under:
  `results/optimizations/<symbol>/<timeframe>/`

### `pine-batch-optimize` — Run Matrix Optimization for Many Pine Files

```bash
hyperview pine-batch-optimize --input-dir strategies/raw --symbols OANDA:XAUUSD OANDA:EURUSD --timeframes 15m 1h
```

- Runs `pine-optimize` for each `pine x symbol x timeframe`.
- Writes aggregate leaderboard files:
  - `results/optimizations/leaderboard.json`
  - `results/optimizations/leaderboard.md`

## Indicators

HyperView ships with **20 wrapped indicators** backed by TA-Lib, plus **4 signal helpers**. You also have direct access to all **150+ TA-Lib functions** via the `to_numpy` / `wrap` conversion helpers.

### Wrapped Indicators

| Category | Functions |
|----------|-----------|
| **Moving Averages** | `ema`, `sma`, `wma` |
| **Momentum** | `rsi`, `macd`, `stochastic`, `stochastic_rsi`, `cci`, `williams_r`, `momentum`, `roc` |
| **Trend** | `adx` (returns ADX, +DI, −DI), `aroon` (returns down, up), `psar` |
| **Volatility** | `atr`, `bollinger_bands` (returns upper, middle, lower) |
| **Volume** | `obv`, `mfi`, `ad`, `vwap` |

### Signal Helpers

| Function | Description |
|----------|-------------|
| `crossed_above(a, b)` | True on bars where `a` crosses above `b` |
| `crossed_below(a, b)` | True on bars where `a` crosses below `b` |
| `barssince(cond)` | Bars since condition was last True |
| `to_unix_timestamp(dt)` | Convert ISO date string to UTC unix timestamp |

### Using TA-Lib Directly

For any of TA-Lib's 150+ functions not wrapped above, call `talib` directly and use the conversion helpers:

```python
import talib
from strategy.indicators import to_numpy, wrap

df["cci"] = wrap(talib.CCI(to_numpy(df["high"]),
                            to_numpy(df["low"]),
                            to_numpy(df["close"]), timeperiod=20), df.index)
```

## Adding Custom Strategies

1. Create a new file in `strategy/` (e.g. `my_strategy.py`)
2. Subclass `BaseStrategy` and implement `generate_signals()`, `default_settings()`, `required_columns()`
3. Decorate the class with `@register_strategy`

Strategies are auto-discovered at startup — no manual imports needed.

```python
from strategy import register_strategy
from strategy.base import BaseStrategy
from strategy.indicators import ema, crossed_above

@register_strategy
class MyStrategy(BaseStrategy):
    strategy_name = "my_strategy"

    def default_settings(self):
        return {"fast_period": 10, "slow_period": 20}

    def required_columns(self):
        return ["time", "open", "high", "low", "close"]

    def generate_signals(self, candles, settings):
        df = self.prepare_candles(candles)

        fast = ema(df["close"], settings["fast_period"])
        slow = ema(df["close"], settings["slow_period"])

        df["buy_signal"] = crossed_above(fast, slow)
        df["sell_signal"] = crossed_above(slow, fast)
        df["in_date_range"] = True
        df["enable_long"] = True
        df["enable_short"] = False

        return df
```

Then use it: `hyperview backtest --symbol NASDAQ:NFLX --strategy my_strategy --sl 5 --tp 5`

## Output Files

Hyperopt updates a strategy preset file in `results/`:

```
results/macd_rsi_presets.json
```

Each file stores one best preset per exact `pair + timeframe + session + adjustment + mode`
combination for that strategy. Re-running hyperopt replaces only the matching entry
and preserves other contexts already saved in the file.

## Backtest Assumptions

The simulator approximates TradingView's intrabar fill behavior:

- **Entry**: Signal-generated market orders fill on the **next bar open**
- **Intrabar path**: If a bar opens closer to its high, path is `open → high → low → close`; closer to its low, path is `open → low → high → close`
- **Position sizing**: 100% of equity per trade, no pyramiding
- **SL/TP exits**: Checked against the intrabar price path within the same bar
