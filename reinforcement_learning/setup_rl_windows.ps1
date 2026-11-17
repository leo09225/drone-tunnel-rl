param(
    [string]$Python = ".\.venv\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $Python)) {
    Write-Error "Python executable not found at $Python"
    exit 1
}

Write-Host "Installing binary RL dependencies..."
& $Python -m pip install setuptools gymnasium pygame-ce
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Installing MiniGrid without rebuilding pygame..."
& $Python -m pip install minigrid --no-deps
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Installing Stable-Baselines3..."
& $Python -m pip install stable-baselines3
exit $LASTEXITCODE
