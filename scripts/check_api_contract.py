import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
CLIENT_ROOT = ROOT / "packages" / "api-client"
COMMITTED_OPENAPI = CLIENT_ROOT / "openapi.json"
COMMITTED_TYPES = CLIENT_ROOT / "src" / "generated" / "schema.ts"
sys.path.insert(0, str(API_ROOT))

from app.main import app  # noqa: E402


def _normalized_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def main() -> None:
    pnpm = shutil.which("pnpm") or shutil.which("pnpm.cmd")
    if pnpm is None:
        raise SystemExit("pnpm is required to check generated API contracts")

    with TemporaryDirectory(prefix="transitops-contract-") as temp_dir:
        temp_root = Path(temp_dir)
        temp_openapi = temp_root / "openapi.json"
        temp_types = temp_root / "schema.ts"
        temp_openapi.write_text(
            json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        subprocess.run(
            [
                pnpm,
                "--dir",
                str(CLIENT_ROOT),
                "exec",
                "openapi-typescript",
                str(temp_openapi),
                "-o",
                str(temp_types),
            ],
            cwd=ROOT,
            check=True,
        )

        drift: list[str] = []
        if not COMMITTED_OPENAPI.exists() or _normalized_text(
            COMMITTED_OPENAPI
        ) != _normalized_text(temp_openapi):
            drift.append(str(COMMITTED_OPENAPI.relative_to(ROOT)))
        if not COMMITTED_TYPES.exists() or _normalized_text(
            COMMITTED_TYPES
        ) != _normalized_text(temp_types):
            drift.append(str(COMMITTED_TYPES.relative_to(ROOT)))
        if drift:
            files = "\n- ".join(drift)
            raise SystemExit(
                f"Generated API contract drift detected:\n- {files}\nRun 'pnpm api:generate'."
            )

    print("Generated API contracts are up to date.")


if __name__ == "__main__":
    main()
