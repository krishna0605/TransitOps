import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.main import app  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export the TransitOps OpenAPI contract."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "packages" / "api-client" / "openapi.json",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    try:
        label = output.relative_to(ROOT)
    except ValueError:
        label = output
    print(f"Wrote {label}")


if __name__ == "__main__":
    main()
