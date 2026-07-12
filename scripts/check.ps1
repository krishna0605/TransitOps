$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv/Scripts/python.exe")) {
    throw "Python environment missing. Run ./scripts/bootstrap.ps1 first."
}

pnpm --dir apps/web lint
pnpm --dir apps/web format:check
pnpm --dir apps/web typecheck
pnpm --dir apps/web test

./.venv/Scripts/python.exe -m ruff check apps/api scripts
./.venv/Scripts/python.exe -m ruff format --check apps/api scripts
./.venv/Scripts/python.exe -m mypy apps/api/app
./.venv/Scripts/python.exe -m pytest apps/api

pnpm --dir apps/web build
Write-Host "All TransitOps scaffold checks passed."
