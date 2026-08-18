#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-local}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
REPO_URL="https://github.com/<org>/tradingview-backtest.git"

if command -v git >/dev/null 2>&1; then
  ORIGIN_URL="$(git config --get remote.origin.url 2>/dev/null || true)"
  if [[ "$ORIGIN_URL" =~ ^git@github\.com:(.+)\.git$ ]]; then
    REPO_URL="https://github.com/${BASH_REMATCH[1]}.git"
  elif [[ "$ORIGIN_URL" =~ ^https://github\.com/.+\.git$ ]]; then
    REPO_URL="$ORIGIN_URL"
  fi
fi

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

run_local() {
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN=python3
  else
    PYTHON_BIN=python
  fi
  "$PYTHON_BIN" -m venv .venv
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -e .
  .venv/bin/python -m hyperview --help >/dev/null
  echo "Bootstrap complete. Run commands with:"
  echo "  .venv/bin/python -m hyperview <command>"
}

run_pipx() {
  require_cmd pipx
  pipx install --force "git+$REPO_URL"
  tradingview-backtest --help >/dev/null
  echo "Bootstrap complete. Run commands with:"
  echo "  tradingview-backtest <command>"
}

run_uvx() {
  require_cmd uvx
  uvx --from "git+$REPO_URL" tradingview-backtest --help >/dev/null
  echo "Bootstrap complete. Run commands with:"
  echo "  uvx --from git+$REPO_URL tradingview-backtest <command>"
}

run_pip() {
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN=python3
  else
    PYTHON_BIN=python
  fi
  "$PYTHON_BIN" -m pip install --upgrade pip
  "$PYTHON_BIN" -m pip install -e .
  "$PYTHON_BIN" -m hyperview --help >/dev/null
  echo "Bootstrap complete. Run commands with:"
  echo "  $PYTHON_BIN -m hyperview <command>"
}

case "$MODE" in
  local) run_local ;;
  pipx) run_pipx ;;
  uvx) run_uvx ;;
  pip) run_pip ;;
  *)
    echo "Unsupported mode: $MODE" >&2
    echo "Usage: ./scripts/bootstrap.sh [local|pipx|uvx|pip]" >&2
    exit 1
    ;;
esac
