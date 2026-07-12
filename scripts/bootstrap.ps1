$ErrorActionPreference = "Stop"

if (-not (Get-Command pnpm -ErrorAction SilentlyContinue)) {
    throw "pnpm is required. Install pnpm 11.7 or use the Codex bundled runtime."
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python 3.12 is required."
}

pnpm install --frozen-lockfile

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

./.venv/Scripts/python.exe -m pip install --upgrade pip
./.venv/Scripts/python.exe -m pip install -r apps/api/requirements.lock
./.venv/Scripts/python.exe -m pip install --no-deps -e apps/api

if (-not (Test-Path "apps/web/.env.local")) {
    Copy-Item "apps/web/.env.example" "apps/web/.env.local"
}

if (-not (Test-Path "apps/api/.env")) {
    Copy-Item "apps/api/.env.example" "apps/api/.env"
}

Write-Host "TransitOps dependencies are ready. Activate .venv and run 'pnpm dev'."
