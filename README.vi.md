# HyperView (Tiếng Việt)

**Biến ý tưởng TradingView thành hệ thống giao dịch có thể kiểm chứng bằng terminal, nhanh và lặp lại được.**

HyperView là bộ công cụ CLI để tải dữ liệu TradingView, backtest strategy Python với hành vi khớp lệnh gần Pine Script, và tối ưu tham số theo quy trình có thể lặp lại.

English version: [README.md](README.md)

## Ủng Hộ Dự Án

Nếu bạn tìm ra strategy hiệu quả từ repo này, đừng ngần ngại **đánh giá 1 sao** và **fork repo** để ủng hộ dự án.

## Pain Points (Vấn Đề Thực Tế)

- Tối ưu thủ công trên chart TradingView chậm, khó lặp lại, khó audit.
- Kết quả giữa Pine và script local dễ lệch nhau do khác giả định fill.
- Dữ liệu, presets và reports bị phân tán (CSV/notebook/script ad-hoc), khó cộng tác.
- Nghiên cứu multi-strategy, multi-pair tốn thời gian nếu không có pipeline chuẩn.

## Giải Pháp

- Một workflow CLI thống nhất: `download -> signal -> backtest -> optimize -> export artifacts`.
- Backtester mô phỏng gần TradingView (entry ở next bar open + intrabar SL/TP path).
- Tự động lưu presets/reports/context để so sánh và chạy lại chính xác.
- Tối ưu input Pine và xuất file Pine đã inject best params.

## Tính Năng Nổi Bật

- Tải dữ liệu lịch sử qua websocket TradingView (tới ~40K bars khi có phiên đăng nhập phù hợp).
- Framework strategy Python + TA-Lib (20 wrapped indicators + gọi trực tiếp TA-Lib).
- Backtest có portfolio aggregate đúng theo combined equity curve.
- Tối ưu SL/TP bằng Optuna (TPE), lưu top presets.
- Pine optimize 2-stage + batch optimize nhiều file strategy.
- Artifacts có cấu trúc rõ ràng (`data/`, `results/`, `strategies/raw/`, `strategies/optimized/`).

## FAQ (Tài Khoản Pro & Tick Data)

### Không có TradingView Pro thì có dùng được không?

Có. Bạn vẫn dùng được các tính năng tải dữ liệu, backtest, optimize mà không cần Pro.  
Thực tế, độ sâu dữ liệu thường thấp hơn với phiên anonymous/chưa xác thực (thường khoảng ~5K bars), còn phiên đã đăng nhập gói phù hợp có thể lấy sâu hơn (tới ~40K bars, tùy điều kiện account/session).

### HyperView có hỗ trợ tick data không?

Không. HyperView chạy theo dữ liệu candle/timeframe (`1m`, `5m`, `15m`, `1h`...), không phải luồng dữ liệu tick-by-tick.

### Dữ liệu `1m` có phải tick data không?

Không. `1m` vẫn là dữ liệu OHLCV đã tổng hợp theo nến, không phải raw ticks.

### Có dùng để kiểm chứng HFT/tick-level được không?

Không theo kiểu native ở kiến trúc hiện tại. Backtester dùng giả định bar-level + intrabar-path, không replay full ticks.

### Có cần TradingView API key không?

Không. Downloader dùng cơ chế websocket/session của TradingView và có thể tận dụng session trình duyệt local nếu có.

## Hiệu Quả Thực Tế

- Rút ngắn vòng lặp nghiên cứu strategy từ thao tác tay sang pipeline tự động.
- Dễ chia sẻ trong team nhờ presets, reports, contexts nhất quán.
- Giảm mismatch khi chuyển từ ý tưởng Pine sang kiểm chứng định lượng.
- Scale tốt hơn cho nghiên cứu multi-strategy, multi-symbol, multi-timeframe.

## Cải Tiến So Với Nhánh Fork Gốc

Các cải tiến trong fork này được triển khai thành các task rõ ràng:

1. **Task chuẩn hóa CLI**
   - Thống nhất command chính: `tradingview-backtest`.
   - Giữ alias tương thích: `hyperview`, `python -m hyperview`.
   - Mục tiêu: giảm friction khi làm việc team + AI CLI.

2. **Task nâng cấp Pine optimize pipeline**
   - Export `.pine` đã tối ưu với best params inject vào default inputs.
   - Đặt tên file compact theo metrics (`np/dd/pf/tc`).
   - Thêm metadata header theo run để dễ audit.

3. **Task batch orchestration**
   - Chạy optimize hàng loạt nhiều file Pine từ `strategies/raw/`.
   - Hỗ trợ chạy theo ma trận symbol/timeframe.
   - Sinh leaderboard để tổng hợp kết quả tốt nhất.

4. **Task chuẩn hóa contract artifacts**
   - Chuẩn thư mục đầu ra:
     - `strategies/raw/`
     - `strategies/optimized/`
     - `results/optimizations/<symbol>/<timeframe>/`
   - Mục tiêu: output xác định, dễ commit/push/audit.

5. **Task automation & onboarding**
   - Thêm bootstrap scripts đa nền tảng (`.cmd`, `.ps1`, `.sh`).
   - Thêm workflow release/build smoke trên GitHub.
   - Bổ sung hướng dẫn làm việc nhanh với Codex/Claude.

## Yêu Cầu Hệ Thống

### Yêu cầu runtime cơ bản

- **Python 3.11+**
- **TA-Lib** — cài tự động qua `pip install`, có pre-built wheels cho các nền tảng phổ biến.
- **rich** — cài tự động để render bảng/panel/progress trong terminal.
- **Firefox** *(tùy chọn)* — dùng session TradingView để tăng giới hạn dữ liệu lịch sử.

### Yêu cầu bổ sung để dùng đầy đủ các cải tiến của fork

- **Git + GitHub CLI (`gh`)** — cần cho release automation, sync fork, và vận hành workflow GitHub.
- **Một trong `uvx` / `pipx` / `pip`** — để dùng các mode cài/chạy portable đã thêm trong fork này.
- **Workspace có quyền ghi** — vì fork này chủ động lưu artifacts ở:
  - `data/`
  - `results/`
  - `strategies/raw/`
  - `strategies/optimized/`

### Baseline verify trước khi chạy nghiêm túc (khuyến nghị)

```bash
python -m unittest discover -s tests -v
python -m hyperview --help
python -m hyperview list-strategies
```

## Cài Đặt & Chạy Mọi Nơi

Command chuẩn khuyến nghị: `tradingview-backtest`.  
Alias tương thích vẫn hoạt động: `tvbacktest`, `hyperview`, và `python -m hyperview`.

### Option A (Khuyến nghị, kiểu npx): `uvx`

```bash
# Chạy trực tiếp từ GitHub (không cần cài lâu dài)
uvx --from git+https://github.com/<org>/tradingview-backtest.git tradingview-backtest --help
```

```bash
# Sau khi package phát hành lên PyPI
uvx tradingview-backtest --help
```

### Option B (kiểu npm -g): `pipx`

```bash
pipx install tradingview-backtest
tradingview-backtest --help
```

### Option C (fallback phổ quát): `pip`

```bash
python -m pip install tradingview-backtest
python -m hyperview --help
```

### Bootstrap Scripts (có sẵn trong repo)

```bash
# Windows (cmd)
scripts\bootstrap.cmd local

# Windows (PowerShell)
.\scripts\bootstrap.ps1 -Mode local

# Linux/macOS
./scripts/bootstrap.sh local
```

## Quick Start (Cho Development)

```bash
# Cài editable (tạo `tradingview-backtest`, `tvbacktest`, `hyperview`)
pip install -e .

# Tải dữ liệu cho cặp cụ thể
tradingview-backtest download-data --pairs NASDAQ:NFLX NASDAQ:AAPL --timeframe 1h --session extended

# Hoặc dùng pairlist trong config cho nhiều timeframe:
tradingview-backtest download-data --timeframe 1h 15m

# Backtest đơn (dùng pairlist trong config)
tradingview-backtest backtest --sl 3.23 --tp 13.06 --mode long

# Hoặc chạy cho symbol cụ thể với preset file từ hyperopt
tradingview-backtest backtest --symbol NASDAQ:NFLX --preset-file results/adx_stochastic_presets.json

# Tối ưu SL/TP
tradingview-backtest hyperopt --mode long

# Liệt kê dữ liệu đã cache và strategies đã đăng ký
tradingview-backtest list-data
tradingview-backtest list-strategies
```

Bạn vẫn có thể chạy qua module: `python -m hyperview`.

Python bytecode được gom vào `.pycache/` ở root, tránh tạo `__pycache__` rải rác trong source.

## Làm Việc Nhanh Với Codex CLI / Claude Code

Repo này tương thích tốt với cả **Codex CLI** và **Claude Code** cho quy trình AI-assisted development.

### 1) Setup một lần

```bash
# Clone repo
git clone https://github.com/hungpixi/tradingview-backtest.git
cd tradingview-backtest

# Bootstrap local env
# Windows:
scripts\bootstrap.cmd local
# Linux/macOS:
./scripts/bootstrap.sh local
```

### 2) Prompt mẫu cho AI CLI

- `"Run pine-batch-optimize for OANDA:XAUUSD on 15m and summarize best result."`
- `"Add a new CLI flag for pine-optimize and include unit tests."`
- `"Refactor hyperview/cli/pine.py but keep command behavior backward-compatible."`
- `"Review this branch for regressions in backtest and pine optimize flow."`

### 3) Verify nhanh trước khi commit

```bash
python -m unittest discover -s tests -v
python -m hyperview --help
python -m hyperview list-strategies
```

### 4) Mẹo để AI làm đúng nhanh hơn

- Nêu rõ mục tiêu + output kỳ vọng (file/report/command cụ thể).
- Luôn yêu cầu chạy verification command trước khi báo hoàn thành.
- Với thay đổi lớn, yêu cầu tách commit theo chủ đề (`feat`, `chore`, `docs`).
- Ưu tiên kiểm chứng bằng CLI thật (`download-data`, `backtest`, `hyperopt`, `pine-optimize`) thay vì chỉ sửa code.

## Cách Hoạt Động

1. **Download** — Kết nối websocket TradingView bằng session cookies hiện có. Hỗ trợ đến 40K bars (khi đủ điều kiện tài khoản), có backfill tự động.
2. **Signal** — Chạy strategy plugin (ví dụ MACD+RSI hoặc ADX+Stochastic) bằng Python + TA-Lib.
3. **Backtest** — Mô phỏng bar-by-bar với giả định fill gần TradingView (entry ở bar tiếp theo, SL/TP intrabar). Multi-pair tạo thêm hàng **PORTFOLIO** aggregate chuẩn.
4. **Hyper-Optimize** — Tối ưu Bayesian (Optuna TPE) cho SL/TP rồi cập nhật preset tốt nhất theo context.

## Output Trên Terminal

Cả backtest và hyperopt đều dùng [rich](https://github.com/Textualize/rich) để hiển thị:

- **Backtest summary** — Bảng có màu với mũi tên tăng/giảm trên các metric quan trọng. Khi chạy nhiều pair sẽ có dòng **PORTFOLIO** tính từ combined equity curve (không phải trung bình cộng đơn giản).
- **Hyperopt results** — Panel header + thống kê data/signals + bảng top-N, cột tham số (SL/TP) được làm nổi bật.

## Bố Cục Repo

```
pyproject.toml              Metadata package & entry point CLI
config.json                 Cấu hình mặc định (timeframe, pairlist, opt ranges)
config.schema.json          JSON Schema cho editor autocomplete/validation
data/                       Dữ liệu candle cache (auto-generated)
results/                    Presets & reports (auto-generated)
strategies/raw/             Pine scripts đầu vào để optimize
strategies/optimized/       Pine scripts đã optimize (filename có metrics)
```

### `strategy/` — Framework Strategy Plugin

```
strategy/
├── __init__.py             Registry & auto-discovery
├── base.py                 BaseStrategy ABC & prepare_candles()
├── indicators.py           TA-Lib wrappers, conversion helpers & signal toolkit
├── adx_stochastic.py       ADX+Stochastic strategy
└── macd_rsi.py             MACD+RSI strategy
```

### `hyperview/` — Core Engine

```
hyperview/
├── __main__.py             Entry point module (python -m hyperview)
├── config.py               Config loader (JSON + CLI overrides + env vars)
├── models.py               Dataclasses dùng chung (CandleRequest, Trade, BacktestMetrics, …)
├── presets.py              Load/save preset tối ưu SL/TP
├── validators.py           Rule validation config & preset
├── runtime.py              Bytecode cache redirection
│
├── cli/                    Router CLI & handlers
│   ├── __init__.py         Argument parser & main() dispatcher
│   ├── formatting.py       Helpers format output (rich tables, arrows)
│   ├── backtest.py         Command backtest
│   ├── download.py         Command download-data
│   ├── hyperopt.py         Command hyperopt
│   └── list.py             list-data & list-strategies
│
├── backtest/
│   └── engine.py           TradingView-like OHLC simulator
│
├── downloader/
│   ├── client.py           Websocket downloader & cache orchestration
│   ├── cache.py            CSV-backed local candle cache
│   ├── credentials.py      Firefox credential extraction
│   ├── session.py          WebSocket chart session manager
│   └── timeframes.py       Timeframe constants & utilities
│
└── hyperopt/
    └── optimizer.py        Bayesian optimizer (Optuna TPE)
```

## Cấu Hình

HyperView nạp mặc định từ `config.json` ở root. CLI flags luôn override giá trị config.

Ví dụ cấu hình:

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

Dùng `--config /path/to/custom.json` để đổi file cấu hình.

### Pairlist

`pairlist` phải theo định dạng `EXCHANGE:SYMBOL`:

```json
"pairlist": [
    "NASDAQ:NFLX",
    "NASDAQ:TSLA",
    "NASDAQ:AAPL",
    "COINBASE:BTCUSD"
]
```

Nếu không truyền `--pairs` hoặc `--symbol`, HyperView dùng pairlist từ config.  
Khi có `--pairs` hoặc `--symbol`, pairlist trong config sẽ bị override cho run đó.

## Tham Chiếu CLI

Ví dụ lệnh có thể dùng `tradingview-backtest` (khuyến nghị) hoặc alias `hyperview`.

## Ghi Chú Migration

- `hyperview` vẫn được giữ để tương thích ngược.
- Command chuẩn mới cho docs/release là `tradingview-backtest`.
- Có thêm alias ngắn `tvbacktest`.

### `download-data` — Tải Dữ Liệu Nến

```bash
# Tải toàn bộ pair trong config
hyperview download-data

# Hoặc chỉ định pairs/timeframes
hyperview download-data --pairs NASDAQ:NFLX NASDAQ:AAPL NASDAQ:TSLA --timeframe 1h 15m --start 2023-01-03
```

| Flag | Bắt buộc | Mặc định | Mô tả |
|------|----------|----------|------|
| `--pairs` | Không | config pairlist | Một hoặc nhiều cặp `EXCHANGE:SYMBOL` |
| `--timeframe` | Không | config | Một hoặc nhiều khung thời gian |
| `--start` / `--end` | Không | — | Khoảng thời gian (ISO format) |
| `--session` | Không | config | `regular` hoặc `extended` |
| `--adjustment` | Không | `splits` | Điều chỉnh giá (`splits`, `dividends`, `none`) |

### `backtest` — Backtest Một Strategy

```bash
# Backtest tất cả pair trong config
hyperview backtest --sl 5.0 --tp 5.0 --mode long --start 2023-01-03

# Hoặc chạy symbol cụ thể với preset file
hyperview backtest --symbol NASDAQ:NFLX --preset-file results/adx_stochastic_presets.json --start 2023-01-03
```

Nếu không truyền `--sl`/`--tp`, HyperView tìm preset phù hợp trong `--preset-file` theo `pair + timeframe + session + adjustment + mode`.

| Flag | Bắt buộc | Mặc định | Mô tả |
|------|----------|----------|------|
| `--symbol` | Không | config pairlist | Cặp `EXCHANGE:SYMBOL` |
| `--sl` | Không* | — | Stop-loss % (*cần nếu không có preset phù hợp) |
| `--tp` | Không* | — | Take-profit % (*cần nếu không có preset phù hợp) |
| `--preset-file` | Không | auto-detected | File preset JSON |
| `--strategy` | Không | config | Tên strategy |
| `--mode` | Không | `long` | `long`, `short`, `both` |
| `--timeframe`, `--session`, `--adjustment`, `--start`, `--end` | Không | config/default | Bộ lọc chuẩn |

### `hyperopt` — Tối Ưu SL/TP

```bash
# Tối ưu toàn bộ pair trong config
hyperview hyperopt --n-trials 300

# Hoặc một symbol cụ thể
hyperview hyperopt --symbol NASDAQ:NFLX --n-trials 300
```

| Flag | Bắt buộc | Mặc định | Mô tả |
|------|----------|----------|------|
| `--symbol` | Không | config pairlist | Cặp `EXCHANGE:SYMBOL` |
| `--sl-min`, `--sl-max` | Không | config | Khoảng tìm kiếm stop-loss % |
| `--tp-min`, `--tp-max` | Không | config | Khoảng tìm kiếm take-profit % |
| `--n-trials` | Không | config | Số trial Bayesian optimization |
| `--objective` | Không | config | `net_profit_pct`, `profit_factor`, `win_rate_pct`, `max_drawdown_pct`, `trade_count` |
| `--top-n` | Không | config | Số candidate top lưu lại |

### `list-data` — Liệt Kê Dataset Đã Cache

```bash
hyperview list-data
```

### `list-strategies` — Liệt Kê Strategies Có Sẵn

```bash
hyperview list-strategies
```

### `pine-optimize` — Tối Ưu Input Pine + Xuất Best Pine

```bash
hyperview pine-optimize --pine-file strategies/raw/smc_swing_strategy.pine --symbol OANDA:XAUUSD --timeframe 15m
```

- Mặc định xuất best Pine vào `strategies/optimized/`.
- Template filename mặc định:
  `{symbol}_{tf}_{strategy}_np{net}_dd{dd}_pf{pf}_tc{trades}.pine`
- Report theo cặp symbol/timeframe nằm tại:
  `results/optimizations/<symbol>/<timeframe>/`

### `pine-batch-optimize` — Chạy Matrix Cho Nhiều Pine Files

```bash
hyperview pine-batch-optimize --input-dir strategies/raw --symbols OANDA:XAUUSD OANDA:EURUSD --timeframes 15m 1h
```

- Chạy `pine-optimize` cho từng tổ hợp `pine x symbol x timeframe`.
- Tạo leaderboard tổng:
  - `results/optimizations/leaderboard.json`
  - `results/optimizations/leaderboard.md`

## Indicators

HyperView có **20 wrapped indicators** dựa trên TA-Lib, cộng thêm **4 signal helpers**.  
Bạn vẫn có thể gọi trực tiếp toàn bộ **150+ TA-Lib functions** qua helpers `to_numpy` / `wrap`.

### Wrapped Indicators

| Nhóm | Functions |
|------|-----------|
| **Moving Averages** | `ema`, `sma`, `wma` |
| **Momentum** | `rsi`, `macd`, `stochastic`, `stochastic_rsi`, `cci`, `williams_r`, `momentum`, `roc` |
| **Trend** | `adx` (trả ADX, +DI, −DI), `aroon` (trả down, up), `psar` |
| **Volatility** | `atr`, `bollinger_bands` (trả upper, middle, lower) |
| **Volume** | `obv`, `mfi`, `ad`, `vwap` |

### Signal Helpers

| Function | Mô tả |
|----------|------|
| `crossed_above(a, b)` | True khi `a` cắt lên `b` |
| `crossed_below(a, b)` | True khi `a` cắt xuống `b` |
| `barssince(cond)` | Số bar kể từ lần gần nhất điều kiện True |
| `to_unix_timestamp(dt)` | Chuyển ISO datetime thành UTC unix timestamp |

### Dùng TA-Lib Trực Tiếp

```python
import talib
from strategy.indicators import to_numpy, wrap

df["cci"] = wrap(talib.CCI(to_numpy(df["high"]),
                            to_numpy(df["low"]),
                            to_numpy(df["close"]), timeperiod=20), df.index)
```

## Thêm Strategy Tùy Chỉnh

1. Tạo file mới trong `strategy/` (ví dụ `my_strategy.py`)
2. Kế thừa `BaseStrategy` và implement `generate_signals()`, `default_settings()`, `required_columns()`
3. Decorate class với `@register_strategy`

Strategies được auto-discover khi startup, không cần import thủ công.

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

Ví dụ gọi: `hyperview backtest --symbol NASDAQ:NFLX --strategy my_strategy --sl 5 --tp 5`

## Output Files

Hyperopt cập nhật preset file theo strategy trong `results/`:

```
results/macd_rsi_presets.json
```

Mỗi file lưu best preset theo đúng context `pair + timeframe + session + adjustment + mode`.  
Chạy lại hyperopt sẽ chỉ thay entry cùng context và giữ nguyên context khác.

## Giả Định Backtest

Simulator mô phỏng intrabar fill gần TradingView:

- **Entry**: market order fill ở **next bar open**
- **Intrabar path**:
  - Nếu open gần high hơn: `open -> high -> low -> close`
  - Nếu open gần low hơn: `open -> low -> high -> close`
- **Position sizing**: dùng 100% equity mỗi lệnh, không pyramiding
- **SL/TP exits**: kiểm tra theo intrabar path ngay trong cùng bar
