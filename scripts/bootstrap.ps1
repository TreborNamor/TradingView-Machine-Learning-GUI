param(
    [ValidateSet("local", "pipx", "uvx", "pip")]
    [string]$Mode = "local"
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Require-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Missing required command: $Name"
    }
}

function Resolve-RepoUrl {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $origin = (git config --get remote.origin.url 2>$null)
        if ($origin) {
            if ($origin -match "^git@github\.com:(.+)\.git$") {
                return "https://github.com/$($Matches[1]).git"
            }
            if ($origin -match "^https://github\.com/.+\.git$") {
                return $origin
            }
        }
    }
    return "https://github.com/<org>/tradingview-backtest.git"
}

function Run-Local {
    Require-Command "python"
    python -m venv .venv
    .\.venv\Scripts\python -m pip install --upgrade pip
    .\.venv\Scripts\python -m pip install -e .
    .\.venv\Scripts\python -m hyperview --help | Out-Null
    Write-Host "Bootstrap complete. Run commands with:"
    Write-Host "  .\.venv\Scripts\python -m hyperview <command>"
}

function Run-Pipx {
    Require-Command "pipx"
    $repoUrl = Resolve-RepoUrl
    pipx install --force "git+$repoUrl"
    tradingview-backtest --help | Out-Null
    Write-Host "Bootstrap complete. Run commands with:"
    Write-Host "  tradingview-backtest <command>"
}

function Run-Uvx {
    Require-Command "uvx"
    $repoUrl = Resolve-RepoUrl
    uvx --from "git+$repoUrl" tradingview-backtest --help | Out-Null
    Write-Host "Bootstrap complete. Run commands with:"
    Write-Host "  uvx --from git+$repoUrl tradingview-backtest <command>"
}

function Run-Pip {
    Require-Command "python"
    python -m pip install --upgrade pip
    python -m pip install -e .
    python -m hyperview --help | Out-Null
    Write-Host "Bootstrap complete. Run commands with:"
    Write-Host "  python -m hyperview <command>"
}

switch ($Mode) {
    "local" { Run-Local; break }
    "pipx" { Run-Pipx; break }
    "uvx" { Run-Uvx; break }
    "pip" { Run-Pip; break }
    default { throw "Unsupported mode: $Mode" }
}
