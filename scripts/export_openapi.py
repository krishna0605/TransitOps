import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
API_ROOT = ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.main import app  # noqa: E402

output = ROOT / "packages" / "api-client" / "openapi.json"
output.write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
print(f"Wrote {output.relative_to(ROOT)}")
